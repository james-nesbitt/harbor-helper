"""
Core domain models for Harbor Helper.
Reflects requirements from SPEC.md and INTENT.md (Safety, Auditability, Peer Review).
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class RequestStatus(str, Enum):
    RECEIVED = "received"
    INTERPRETED = "interpreted"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class ActionKind(str, Enum):
    CREATE_PROJECT = "harbor-manage-projects"
    CREATE_ROBOT = "harbor-new-robot"


@dataclass(frozen=True)
class RequestContext:
    """Metadata about where the request came from."""

    raw_text: str
    requester_id: str
    channel_id: str
    thread_ts: str
    jira_key: Optional[str] = None


@dataclass(frozen=True)
class HarborRegistryConfig:
    """Config for a single Harbor registry instance."""

    nickname: str
    url: str
    user: str
    password: str


@dataclass
class ProposedAction:
    """The LLM's interpretation of what needs to change."""

    kind: ActionKind
    target_id: str  # The nickname of the service/registry to target
    summary: str
    details: str
    reasoning: str
    payload: Dict[str, Any]


@dataclass
class ExecutionResult:
    """Result of running an action against Harbor."""

    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
