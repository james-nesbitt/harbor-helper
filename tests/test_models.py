"""Unit tests for data models."""

import pytest
from harbor_helper.models import (
    RequestContext,
    ProposedAction,
    ActionKind,
    ExecutionResult,
)


def test_request_context_frozen():
    r = RequestContext(
        raw_text="create project x",
        requester_id="U123",
        channel_id="C1",
        thread_ts="T1",
    )
    with pytest.raises(Exception):
        r.raw_text = "other"  # type: ignore


def test_proposed_action_payload():
    p = ProposedAction(
        kind=ActionKind.CREATE_PROJECT,
        target_id="dev",
        summary="Create project",
        details="Details",
        reasoning="Reasoning",
        payload={"project_name": "foo", "public": False},
    )
    assert p.payload["project_name"] == "foo"


def test_execution_result_failed():
    r = ExecutionResult(success=False, data={}, error="Something went wrong")
    assert r.success is False
    assert r.error == "Something went wrong"
