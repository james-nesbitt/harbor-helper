"""
Core task coordination logic.
Implements the workflow defined in SPEC §5 and INTENT.md.
"""

import logging
from typing import List
from .models import RequestContext, ProposedAction, ExecutionResult
from .interfaces import JIRAClient, HarborClient, Messenger, Interpreter

logger = logging.getLogger(__name__)


class HarborHelper:
    def __init__(
        self,
        interpreter: Interpreter,
        jira: JIRAClient,
        harbor: HarborClient,
        messenger: Messenger,
        approved_engineers: List[str],
    ):
        self.interpreter = interpreter
        self.jira = jira
        self.harbor = harbor
        self.messenger = messenger
        self.approved_engineers = approved_engineers

    def handle_request(self, context: RequestContext):
        """Main entry point for a new Slack message."""

        # 1. Authorization Check (INTENT: Safety first)
        if context.requester_id not in self.approved_engineers:
            self.messenger.reply(
                context, "Unauthorized: You are not on the approved ops engineer list."
            )
            return

        # 1.5. Check for JIRA project (SPEC Requirement 8 and workflow)
        # Every request MUST be associated with an existing JIRA ticket from the 'PRODENG' or 'IT' projects.
        is_valid_project = context.jira_key and (
            context.jira_key.startswith("PRODENG-")
            or context.jira_key.startswith("IT-")
        )
        if not is_valid_project:
            self.messenger.reply(
                context,
                "Error: A JIRA ticket ID in the 'PRODENG' or 'IT' projects is required to process this request. "
                "Please provide a ticket ID (e.g., PRODENG-123 or IT-456).",
            )
            return

        # 2. Audit Trail Start (SPEC §5)
        # Ensure we have the ticket key (the client will just return it if it already exists in context)
        jira_key = self.jira.create_ticket(context)
        context = RequestContext(**{**context.__dict__, "jira_key": jira_key})
        self.jira.update_status(jira_key, "IN_PROGRESS")

        try:
            # 3. Interpretation (Embedded LLM)
            action = self.interpreter.interpret(context.raw_text)

            # 3.5. Existence Check (INTENT: Be sure operation is correct)
            if self.harbor.resource_exists(
                action.kind, action.target_id, action.payload
            ):
                msg = f"Validation Error: The requested resource already exists on '{action.target_id}'."
                self.messenger.reply(context, msg)
                self.jira.add_comment(jira_key, msg)
                self.jira.update_status(jira_key, "REJECTED")
                return

            # Log reasoning to JIRA (INTENT: Auditability)
            self.jira.add_comment(jira_key, f"LLM Reasoning: {action.reasoning}")

            # 4. Describe & Seek Approval (NFR 2 & 3)
            # This is where the flow normally pauses for a Slack interaction.
            self.messenger.ask_for_approval(context, action)

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.messenger.reply(
                context, f"I encountered an error interpreting your request: {e}"
            )
            self.jira.add_comment(jira_key, f"Failure during interpretation: {e}")
            self.jira.update_status(jira_key, "FAILED")

    def handle_approval(
        self, context: RequestContext, action: ProposedAction, approver_id: str
    ):
        """Called when a Slack button or JIRA transition triggers an approval."""
        jira_key = context.jira_key

        # NFR 3: Peer Review (approver != requester)
        if approver_id == context.requester_id:
            self.messenger.reply(
                context,
                "Error: Self-approval is not allowed. Please have a peer review.",
            )
            return

        self.jira.add_comment(jira_key, f"Approved by {approver_id}. Executing action.")
        self.jira.update_status(jira_key, "EXECUTING")

        # 5. Execution (NFR 1: Safe execution)
        result = self.harbor.execute(action)

        if result.success:
            self._handle_success(context, action, result)
        else:
            self._handle_failure(context, result)

    def handle_rejection(
        self, context: RequestContext, action: ProposedAction, rejecter_id: str
    ):
        """Called when a Slack button or JIRA transition triggers a rejection."""
        jira_key = context.jira_key
        self.messenger.reply(context, f"Request rejected by <@{rejecter_id}>.")
        self.jira.add_comment(jira_key, f"Rejected by {rejecter_id}.")
        self.jira.update_status(jira_key, "REJECTED")

    def _handle_success(
        self, context: RequestContext, action: ProposedAction, result: ExecutionResult
    ):
        jira_key = context.jira_key
        # NFR 4: Credentials ONLY in DM
        if "token" in result.data or "secret" in result.data:
            creds = result.data.get("token") or result.data.get("secret")
            self.messenger.send_dm(
                context.requester_id, f"Credentials for {action.summary}: `{creds}`"
            )
            msg = "Execution complete. I've sent the credentials to you via DM."
        else:
            msg = f"Execution complete. Result: {result.data}"

        self.messenger.reply(context, msg)
        self.jira.add_comment(jira_key, f"Success: {msg}")
        self.jira.update_status(jira_key, "COMPLETED")

    def _handle_failure(self, context: RequestContext, result: ExecutionResult):
        self.messenger.reply(context, f"Execution failed: {result.error}")
        self.jira.add_comment(context.jira_key, f"Execution Error: {result.error}")
        self.jira.update_status(context.jira_key, "FAILED")
