import http.client
import json
import os
import sys
from urllib.parse import urlparse


DEFAULT_BASE_URL = "http://host.docker.internal:8880"
EXPECTED_STATUSES = [401, 400, 200]


def post_json(base_url: str, path: str, payload: dict, headers: dict | None = None) -> tuple[int, str]:
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"unsupported URL scheme: {parsed.scheme}")
    if not parsed.hostname:
        raise ValueError("DEMO_API_BASE_URL must include a hostname")

    connection_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    connection = connection_class(parsed.hostname, port, timeout=10)

    body = json.dumps(payload)
    request_headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(body.encode("utf-8"))),
    }
    if headers:
        request_headers.update(headers)

    try:
        connection.request("POST", path, body=body, headers=request_headers)
        response = connection.getresponse()
        response_body = response.read().decode("utf-8", errors="replace")
        return response.status, response_body
    finally:
        connection.close()


def main() -> int:
    base_url = os.getenv("DEMO_API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    cases = [
        (
            "missing authorization",
            {"email": "test@test.com", "age": 25},
            {},
            401,
        ),
        (
            "invalid age type",
            {"email": "test@test.com", "age": "25"},
            {"Authorization": "Bearer demo"},
            400,
        ),
        (
            "valid demo user",
            {"email": "test@test.com", "age": 25},
            {"Authorization": "Bearer demo"},
            200,
        ),
    ]

    print(f"Target API: {base_url}")
    actual_statuses = []

    for label, payload, headers, expected_status in cases:
        try:
            actual_status, response_body = post_json(base_url, "/demo/users", payload, headers=headers)
        except Exception as exc:
            actual_status = None
            response_body = f"{type(exc).__name__}: {exc}"

        actual_statuses.append(actual_status)
        print(f"Request: {label}")
        print(f"Expected status: {expected_status}")
        print(f"Actual status: {actual_status}")
        print(f"Response body: {response_body}")

    return 0 if actual_statuses == EXPECTED_STATUSES else 1


if __name__ == "__main__":
    sys.exit(main())
