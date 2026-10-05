import importlib.util
import json
import os
from decimal import Decimal
from types import SimpleNamespace

import boto3
from moto import mock_aws


os.environ["TABLE_NAME"] = "GlobalProductAPI-Products"
os.environ["AWS_DEFAULT_REGION"] = "ap-south-1"


def load_lambda_module():
    spec = importlib.util.spec_from_file_location(
        "lambda_function",
        "lambda/lambda_function.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_test_table():
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="ap-south-1"
    )

    return dynamodb.create_table(
        TableName="GlobalProductAPI-Products",
        KeySchema=[
            {"AttributeName": "id", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "id", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST",
    )


@mock_aws
def test_get_product_success():
    table = create_test_table()

    table.put_item(
        Item={
            "id": "test-001",
            "name": "Test Product",
            "price": Decimal("99.99"),
            "category": "Demo",
        }
    )

    module = load_lambda_module()

    event = {
        "httpMethod": "GET",
        "path": "/products/test-001",
        "pathParameters": {"id": "test-001"},
        "stageVariables": {"apiVersion": "v2"},
        "requestContext": {},
    }

    context = SimpleNamespace(
        aws_request_id="test-request-001"
    )

    result = module.lambda_handler(event, context)

    assert result["statusCode"] == 200

    body = json.loads(result["body"])

    assert body["id"] == "test-001"
    assert body["name"] == "Test Product"
    assert body["apiVersion"] == "v2"


@mock_aws
def test_get_product_not_found():
    create_test_table()

    module = load_lambda_module()

    event = {
        "httpMethod": "GET",
        "path": "/products/missing-product",
        "pathParameters": {"id": "missing-product"},
        "stageVariables": {"apiVersion": "v1"},
        "requestContext": {},
    }

    context = SimpleNamespace(
        aws_request_id="test-request-002"
    )

    result = module.lambda_handler(event, context)

    assert result["statusCode"] == 404

    body = json.loads(result["body"])

    assert body["message"] == "Product not found"
