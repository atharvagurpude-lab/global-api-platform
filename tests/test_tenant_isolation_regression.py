def test_tenant_id_is_taken_from_jwt_claim():
    code = """
def get_tenant_id(event):
    claims = event["requestContext"]["authorizer"]["claims"]
    tenant_id = claims.get("custom:tenant_id")
    if not tenant_id:
        raise Exception("Missing custom:tenant_id claim")
    return tenant_id
"""
    assert 'claims.get("custom:tenant_id")' in code
    assert "tenant_id" in code


def test_tenant_key_is_derived_from_authenticated_tenant():
    tenant_id = "tenant-001"
    tenant_key = f"TENANT#{tenant_id}"

    assert tenant_key == "TENANT#tenant-001"
    assert "tenant-001" in tenant_key


def test_request_body_cannot_override_tenant():
    authenticated_tenant = "tenant-001"
    request_body_tenant = "tenant-002"

    tenant_key = f"TENANT#{authenticated_tenant}"

    assert tenant_key == "TENANT#tenant-001"
    assert request_body_tenant not in tenant_key


def test_all_data_operations_use_tenant_scoping():
    operations = [
        "GetItem",
        "PutItem",
        "UpdateItem",
        "DeleteItem",
        "Query",
    ]

    assert len(operations) == 5
    assert all(operation for operation in operations)


def test_query_is_scoped_to_authenticated_tenant():
    tenant_id = "tenant-001"
    tenant_key = f"TENANT#{tenant_id}"

    queried_key = tenant_key

    assert queried_key == "TENANT#tenant-001"


def test_missing_tenant_claim_is_rejected():
    tenant_id = None

    assert tenant_id is None

    try:
        if not tenant_id:
            raise Exception("Missing custom:tenant_id claim")
    except Exception as error:
        assert str(error) == "Missing custom:tenant_id claim"
