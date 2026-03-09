from harbor_helper.app import HarborHelper
from harbor_helper.models import (
    RequestContext,
    ProposedAction,
    ActionKind,
    ExecutionResult,
)


def test_unauthorized_user_rejection(
    mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
):
    helper = HarborHelper(
        mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
    )
    ctx = RequestContext("create project", "attacker", "chan-1", "ts-1")

    helper.handle_request(ctx)

    # Verify: Rejection message sent, JIRA never touched
    args, _ = mock_messenger.reply.call_args
    assert args[0] == ctx
    assert "Unauthorized" in args[1]
    mock_jira.create_ticket.assert_not_called()


def test_peer_review_enforcement(
    mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
):
    helper = HarborHelper(
        mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
    )
    ctx = RequestContext(
        "new project", "alice", "chan-1", "ts-1", jira_key="PRODENG-123"
    )
    action = ProposedAction(ActionKind.CREATE_PROJECT, "sum", "det", "re", {})

    # Alice tries to approve her own request
    helper.handle_approval(ctx, action, approver_id="alice")

    # Verify: Harbor never executed, error message sent
    mock_harbor.execute.assert_not_called()
    args, _ = mock_messenger.reply.call_args
    assert args[0] == ctx
    assert "Self-approval is not allowed" in args[1]


def test_credential_privacy_dm(
    mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
):
    helper = HarborHelper(
        mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
    )
    ctx = RequestContext("new robot", "alice", "chan-1", "ts-1", jira_key="PRODENG-123")
    action = ProposedAction(ActionKind.CREATE_ROBOT, "sum", "det", "re", {})

    # Mock Harbor returning a secret
    mock_harbor.execute.return_value = ExecutionResult(
        success=True, data={"name": "robot1", "secret": "very-secret-token"}
    )

    helper.handle_approval(ctx, action, approver_id="bob")  # Peer approval

    # Verify: Secret is in the DM, but NOT in the public reply or JIRA comment
    mock_messenger.send_dm.assert_called_once()
    assert "very-secret-token" in mock_messenger.send_dm.call_args[0][1]

    # Public channel reply should NOT contain the secret
    public_msg = mock_messenger.reply.call_args[0][1]
    assert "very-secret-token" not in public_msg

    # JIRA should NOT contain the secret
    jira_comment = mock_jira.add_comment.call_args[0][1]
    assert "very-secret-token" not in jira_comment


def test_fail_closed_on_interpretation_error(
    mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
):
    helper = HarborHelper(
        mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
    )
    ctx = RequestContext("gibberish", "alice", "chan-1", "ts-1")

    # LLM fails to interpret
    mock_interpreter.interpret.side_effect = ValueError("I cannot understand this")

    helper.handle_request(ctx)

    # Verify: Ticket created but marked as FAILED in JIRA, and never got to approval phase
    mock_jira.create_ticket.assert_called_once()
    mock_jira.update_status.assert_any_call("PRODENG-123", "FAILED")
    args, _ = mock_messenger.reply.call_args
    assert args[0].jira_key == "PRODENG-123"
    assert "error interpreting" in args[1]


def test_jira_project_enforcement(
    mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
):
    helper = HarborHelper(
        mock_interpreter, mock_jira, mock_harbor, mock_messenger, approved_engineers
    )

    # Request with an invalid JIRA key (not PRODENG)
    ctx = RequestContext(
        "create project", "alice", "chan-1", "ts-1", jira_key="OTHER-123"
    )

    helper.handle_request(ctx)

    # Verify: Rejection message sent, JIRA never touched
    args, _ = mock_messenger.reply.call_args
    assert args[0] == ctx
    assert "Only tickets in the 'PRODENG' project are supported" in args[1]
    mock_jira.create_ticket.assert_not_called()

    # Request with a valid JIRA key (PRODENG)
    ctx_valid = RequestContext(
        "create project", "alice", "chan-1", "ts-1", jira_key="PRODENG-456"
    )
    helper.handle_request(ctx_valid)

    # Verify: Ticket "created" (re-used) and interpretation continues
    mock_jira.create_ticket.assert_called_once()
    mock_interpreter.interpret.assert_called_once()
