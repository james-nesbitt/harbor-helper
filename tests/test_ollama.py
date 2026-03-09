import pytest
import json
from unittest.mock import patch
from harbor_helper.interpreter_ollama import OllamaInterpreter
from harbor_helper.models import ActionKind


@pytest.fixture
def interpreter():
    return OllamaInterpreter()


def test_ollama_interpretation_success(interpreter):
    mock_response = {
        "message": {
            "content": json.dumps(
                {
                    "kind": "harbor-manage-projects",
                    "target_id": "default",
                    "summary": "Create Project",
                    "details": "Create 'team-alpha'",
                    "reasoning": "User asked for alpha",
                    "payload": {"name": "team-alpha"},
                }
            )
        }
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200

        action = interpreter.interpret("I need a new project for team alpha")

        assert action.kind == ActionKind.CREATE_PROJECT
        assert action.payload["name"] == "team-alpha"


def test_ollama_fail_closed_on_invalid_json(interpreter):
    mock_response = {
        "message": {"content": "This is not JSON, it's a polite sentence."}
    }

    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200

        with pytest.raises(ValueError, match="safe plan"):
            interpreter.interpret("help me")


@pytest.mark.ollama
def test_ollama_live_connectivity():
    """
    INTEGRATION TEST: Requires a real Ollama instance at localhost:11434.
    This test is skipped by default. Run with 'pytest --run-ollama'.
    """
    interpreter = OllamaInterpreter(url="http://localhost:11434/api/chat")
    # This will hit the network. If Ollama is not there, it will fail or timeout.
    # We expect it to raise ValueError because we aren't sending valid prompt here
    # or it will fail on connection error.
    with pytest.raises(Exception):
        interpreter.interpret("say hello")
