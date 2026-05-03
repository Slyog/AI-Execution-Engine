import http.client
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_ENGINE_URL = "http://localhost:8000"
DEFAULT_CODE_PATH = Path(__file__).with_name("test_demo_users_local.py")


def post_sandbox_run(engine_url: str, code: str) -> tuple[int, str]:
    parsed = urlparse(engine_url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"unsupported URL scheme: {parsed.scheme}")
    if not parsed.hostname:
        raise ValueError("ENGINE_API_BASE_URL must include a hostname")

    connection_class = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    connection = connection_class(parsed.hostname, port, timeout=30)
    body = json.dumps({"code": code, "allow_network": True})
    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(body.encode("utf-8"))),
    }

    try:
        connection.request("POST", "/sandbox-runs", body=body, headers=headers)
        response = connection.getresponse()
        response_body = response.read().decode("utf-8", errors="replace")
        return response.status, response_body
    finally:
        connection.close()


def main() -> int:
    engine_url = os.getenv("ENGINE_API_BASE_URL", DEFAULT_ENGINE_URL).rstrip("/")
    code_path = Path(os.getenv("DEMO_USERS_CODE_PATH", str(DEFAULT_CODE_PATH)))
    code = code_path.read_text(encoding="utf-8")

    print(f"Target engine: {engine_url}")
    print(f"Sandbox code: {code_path}")

    status, response_body = post_sandbox_run(engine_url, code)
    print(f"Endpoint status: {status}")
    print(f"Response body: {response_body}")

    if status != 200:
        return 1

    try:
        payload = json.loads(response_body)
    except json.JSONDecodeError:
        return 1

    stdout = payload.get("stdout", "")
    expected_lines = ["Actual status: 401", "Actual status: 400", "Actual status: 200"]
    return 0 if payload.get("status") == "completed" and all(line in stdout for line in expected_lines) else 1


if __name__ == "__main__":
    sys.exit(main())
