import pytest
from unittest.mock import MagicMock
from harbor_helper.interfaces import JIRAClient, HarborClient, Messenger, Interpreter


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
