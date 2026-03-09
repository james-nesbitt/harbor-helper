import pytest
from unittest.mock import MagicMock
from harbor_helper.interfaces import JIRAClient, HarborClient, Messenger, Interpreter


def pytest_addoption(parser):
    parser.addoption(
        "--run-ollama",
        action="store_true",
        default=False,
        help="run tests that require a live Ollama instance",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-ollama"):
        return
    skip_ollama = pytest.mark.skip(reason="need --run-ollama option to run")
    for item in items:
        if "ollama" in item.keywords:
            item.add_marker(skip_ollama)


@pytest.fixture
def mock_jira():
    mock = MagicMock(spec=JIRAClient)
    mock.create_ticket.return_value = "PRODENG-123"
    return mock


@pytest.fixture
def mock_harbor():
    return MagicMock(spec=HarborClient)


@pytest.fixture
def mock_messenger():
    return MagicMock(spec=Messenger)


@pytest.fixture
def mock_interpreter():
    return MagicMock(spec=Interpreter)


@pytest.fixture
def approved_engineers():
    return ["alice", "bob"]
