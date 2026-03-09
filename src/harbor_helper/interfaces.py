"""
Abstract interfaces for external service integrations.
Allows for mocking and multi-service support (NFR 7).
"""

from typing import Protocol
from .models import RequestContext, ProposedAction, ExecutionResult


class JIRAClient(Protocol):
    """SPEC §1: Comment on and update related JIRA tickets."""

    def create_ticket(self, context: RequestContext) -> str: ...
    def add_comment(self, ticket_key: str, comment: str) -> None: ...
    def update_status(self, ticket_key: str, status: str) -> None: ...


class HarborClient(Protocol):
    """SPEC Feature set 1: Harbor OCI registries."""

    def execute(self, action: ProposedAction) -> ExecutionResult: ...

    def resource_exists(
        self, kind: ActionKind, target_id: str, payload: Dict[str, Any]
    ) -> bool: ...


class Messenger(Protocol):
    """SPEC §1: Communication via Slack."""

    def reply(self, context: RequestContext, message: str) -> None: ...
    def send_dm(self, user_id: str, message: str) -> None: ...
    def ask_for_approval(
        self, context: RequestContext, action: ProposedAction
    ) -> None: ...


class Interpreter(Protocol):
    """SPEC §1: Interpret requests using an embedded LLM."""

    def interpret(self, raw_text: str) -> ProposedAction: ...
