import logging
import json
import os
import boto3
logger = logging.getLogger()
logger.setLevel(logging.INFO)
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def decimal_to_number(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {k: decimal_to_number(v) for k, v in value.items()}
    if isinstance(value, list):
        return [decimal_to_number(v) for v in value]
    return value


def response(status_code, body=None, deprecated=False):
    headers = {
        "Content-Type": "application/json"
    }

    if deprecated:
        headers["Deprecation"] = "true"
        headers["Sunset"] = "Wed, 30 Dec 2026 23:59:59 GMT"

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(decimal_to_number(body)) if body is not None else ""
    }


def lambda_handler(event, context):
    logger.info(json.dumps({
        "event": "api_request",
        "request_id": context.aws_request_id,
        "http_method": event.get("httpMethod", ""),
        "path": event.get("path", ""),
        "api_version": (event.get("stageVariables") or {}).get("apiVersion", "v1")
    }))

    stage_variables = event.get("stageVariables") or {}
    api_version = stage_variables.get("apiVersion", "v1")
    deprecated_v1 = api_version == "v1"

    method = event.get("httpMethod", "")

    # Admin-only authorization for POST /products
    claims = ((event.get("requestContext") or {}).get("authorizer") or {}).get("claims") or {}
    groups = claims.get("cognito:groups", "")
    if isinstance(groups, str):
        groups = [g.strip() for g in groups.split(",")]

    if method == "POST" and "Admin" not in groups:
        return response(403, {"message": "Admin group required"}, deprecated=deprecated_v1)

    path_parameters = event.get("pathParameters") or {}
    product_id = path_parameters.get("id")

    # API version is controlled by the API Gateway stage variable.
    stage_variables = event.get("stageVariables") or {}
    api_version = stage_variables.get("apiVersion", "v1")

    body = {}
    if event.get("body"):
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return response(400, {"message": "Invalid JSON body"}, deprecated=deprecated_v1)

    # GET /products
    if method == "GET" and not product_id:
        result = table.scan()
        items = result.get("Items", [])

        if api_version == "v2":
            return response(200, {
                "apiVersion": "v2",
                "products": items
            })

        return response(200, items, deprecated=deprecated_v1)

    # GET /products/{id}
    if method == "GET" and product_id:
        result = table.get_item(Key={"id": product_id})

        if "Item" not in result:
            return response(404, {"message": "Product not found"}, deprecated=deprecated_v1)

        item = result["Item"]

        if api_version == "v2":
            item["apiVersion"] = "v2"

        return response(200, item, deprecated=deprecated_v1)

    # POST /products
    if method == "POST" and not product_id:
        required_fields = ["name", "price", "category"]

        if not all(field in body for field in required_fields):
            return response(
                400,
                {"message": "name, price and category are required"}
            )

        if "id" not in body:
            return response(400, {"message": "id is required"}, deprecated=deprecated_v1)

        item = {
            "id": body["id"],
            "name": body["name"],
            "price": Decimal(str(body["price"])),
            "category": body["category"]
        }

        table.put_item(Item=item)

        return response(201, item, deprecated=deprecated_v1)

    # PUT /products/{id}
    if method == "PUT" and product_id:
        required_fields = ["name", "price", "category"]

        if not all(field in body for field in required_fields):
            return response(
                400,
                {"message": "name, price and category are required"}
            )

        result = table.get_item(Key={"id": product_id})

        if "Item" not in result:
            return response(404, {"message": "Product not found"}, deprecated=deprecated_v1)

        table.update_item(
            Key={"id": product_id},
            UpdateExpression="SET #n = :name, price = :price, category = :category",
            ExpressionAttributeNames={
                "#n": "name"
            },
            ExpressionAttributeValues={
                ":name": body["name"],
                ":price": Decimal(str(body["price"])),
                ":category": body["category"]
            }
        )

        updated = table.get_item(Key={"id": product_id})

        return response(200, updated["Item"], deprecated=deprecated_v1)

    # DELETE /products/{id}
    if method == "DELETE" and product_id:
        result = table.get_item(Key={"id": product_id})

        if "Item" not in result:
            return response(404, {"message": "Product not found"}, deprecated=deprecated_v1)

        table.delete_item(Key={"id": product_id})

        return response(204, deprecated=deprecated_v1)

    return response(405, {"message": "Method not allowed"}, deprecated=deprecated_v1)
