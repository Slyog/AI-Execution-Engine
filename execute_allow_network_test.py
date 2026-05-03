from unittest.mock import patch

from app import ExecuteRunRequest, execute_tool


class FakeRequest:
    headers = {}


class FakeSessionManager:
    def create_session(self, label):
        return {"id": "session-1"}


class FakeRunManager:
    def __init__(self):
        self.allow_network = None

    def execute_run(self, session_id, code, allow_network=False):
        self.allow_network = allow_network
        return {
            "status": "completed",
            "result": {
                "stdout": "ok\n",
                "stderr": "",
                "exit_code": 0,
                "timed_out": False,
                "duration_ms": 1,
            },
        }


def test_execute_forwards_allow_network() -> None:
    fake_run_manager = FakeRunManager()

    with (
        patch("app.API_KEY", None),
        patch("app.session_manager", FakeSessionManager()),
        patch("app.run_manager", fake_run_manager),
    ):
        response = execute_tool(
            ExecuteRunRequest(code="print('ok')", allow_network=True),
            FakeRequest(),
        )

    assert fake_run_manager.allow_network is True
    assert response["stdout"] == "ok\n"


if __name__ == "__main__":
    test_execute_forwards_allow_network()
    print("execute allow_network tests passed")
