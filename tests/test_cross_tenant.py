import os
import sys
import requests
import boto3

API_URL = os.environ["API_URL"]
API_KEY = os.environ["API_KEY"]

COGNITO_CLIENT_ID = os.environ["COGNITO_CLIENT_ID"]
COGNITO_USERNAME = os.environ["COGNITO_USERNAME"]
COGNITO_PASSWORD = os.environ["COGNITO_PASSWORD"]

cognito = boto3.client("cognito-idp", region_name="ap-south-1")

auth = cognito.initiate_auth(
    ClientId=COGNITO_CLIENT_ID,
    AuthFlow="USER_PASSWORD_AUTH",
    AuthParameters={
        "USERNAME": COGNITO_USERNAME,
        "PASSWORD": COGNITO_PASSWORD
    }
)

ID_TOKEN = auth["AuthenticationResult"]["IdToken"]

headers = {
    "Authorization": f"Bearer {ID_TOKEN}",
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

tests = []


def check(name, passed, details):
    tests.append((name, passed, details))
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} - {details}")


# 1. Cross-tenant read
r = requests.get(
    f"{API_URL}?tenant_id=tenant-002",
    headers=headers
)
data = r.json()

check(
    "Cross-tenant read",
    r.status_code == 200 and data.get("tenant_key") == "TENANT#tenant-001",
    f"HTTP {r.status_code}, tenant={data.get('tenant_key')}"
)


# 2. Cross-tenant update
r = requests.put(
    API_URL,
    headers=headers,
    json={
        "tenant_id": "tenant-002",
        "record_id": "record-002",
        "data": "CI-CROSS-TENANT-ATTACK"
    }
)
data = r.json()

check(
    "Cross-tenant update",
    r.status_code == 200 and data.get("tenant_key") == "TENANT#tenant-001",
    f"HTTP {r.status_code}, tenant={data.get('tenant_key')}"
)


# 3. Cross-tenant delete
r = requests.delete(
    API_URL,
    headers=headers,
    json={
        "tenant_id": "tenant-002",
        "record_id": "record-002"
    }
)
data = r.json()

check(
    "Cross-tenant delete",
    r.status_code == 200 and data.get("tenant_key") == "TENANT#tenant-001",
    f"HTTP {r.status_code}, tenant={data.get('tenant_key')}"
)


# 4. Cross-tenant query
r = requests.post(
    API_URL,
    headers=headers,
    json={
        "operation": "QUERY",
        "tenant_id": "tenant-002"
    }
)
data = r.json()

check(
    "Cross-tenant query",
    r.status_code == 200 and data.get("tenant_key") == "TENANT#tenant-001",
    f"HTTP {r.status_code}, tenant={data.get('tenant_key')}"
)


# 5. Tampered JWT
tampered_token = ID_TOKEN[:100] + "X" + ID_TOKEN[101:]

tampered_headers = {
    "Authorization": f"Bearer {tampered_token}",
    "x-api-key": API_KEY
}

r = requests.get(
    API_URL,
    headers=tampered_headers
)

check(
    "Tampered JWT",
    r.status_code in (401, 403),
    f"HTTP {r.status_code}"
)


failed = [test for test in tests if not test[1]]

print("\n========================================")

if failed:
    print("CROSS-TENANT ISOLATION TESTS: FAILED")
    sys.exit(1)
else:
    print("CROSS-TENANT ISOLATION TESTS: PASSED")
    print("All isolation tests passed.")
