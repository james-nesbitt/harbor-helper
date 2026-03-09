"""
Mock implementations of external services for local development and testing.
Provides interactive and non-interactive simulations of Slack, JIRA, and Harbor.
"""

import json
import logging
from typing import List, Optional
from .models import RequestContext, ProposedAction, ExecutionResult, ActionKind

logger = logging.getLogger(__name__)

class MockJiraClient:
    def __init__(self, project_key: str = "PRODENG"):
        self.project_key = project_key
        self.tickets = {}
        self.counter = 100

    def create_ticket(self, context: RequestContext) -> str:
        if context.jira_key:
            logger.info(f"[MOCK JIRA] Using existing ticket {context.jira_key}")
            return context.jira_key
        
        ticket_id = f"{self.project_key}-{self.counter}"
        self.counter += 1
        self.tickets[ticket_id] = {"comments": [], "status": "OPEN"}
        logger.info(f"[MOCK JIRA] Created new ticket {ticket_id}")
        return ticket_id

    def add_comment(self, ticket_key: str, comment: str) -> None:
        logger.info(f"[MOCK JIRA] Added comment to {ticket_key}: {comment}")
        if ticket_key in self.tickets:
            self.tickets[ticket_key]["comments"].append(comment)

    def update_status(self, ticket_key: str, status: str) -> None:
        logger.info(f"[MOCK JIRA] Updated status of {ticket_key} to {status}")
        if ticket_key in self.tickets:
            self.tickets[ticket_key]["status"] = status


class MockHarborClient:
    def execute(self, action: ProposedAction) -> ExecutionResult:
        logger.info(f"[MOCK HARBOR] Target Registry: {action.target_id}")
        logger.info(f"[MOCK HARBOR] Executing action: {action.kind}")
        logger.info(f"[MOCK HARBOR] Payload: {json.dumps(action.payload, indent=2)}")
        
        if action.kind == ActionKind.CREATE_PROJECT:
            return ExecutionResult(
                success=True, 
                data={"location": f"/api/v2.0/projects/{action.payload.get('project_name', 'new-project')}"}
            )
        elif action.kind == ActionKind.CREATE_ROBOT:
            return ExecutionResult(
                success=True, 
                data={"id": 123, "name": action.payload.get("name"), "secret": "mock-robot-secret-123"}
            )
        
        return ExecutionResult(success=False, data={}, error=f"Unknown kind {action.kind}")


class MockMessenger:
    def __init__(self, interactive: bool = True):
        self.interactive = interactive

    def reply(self, context: RequestContext, message: str) -> None:
        print(f"\n[MOCK SLACK] Thread {context.thread_ts} (Channel {context.channel_id}):")
        print(f" > {message}")

    def send_dm(self, user_id: str, message: str) -> None:
        print(f"\n[MOCK SLACK] Private DM to {user_id}:")
        print(f" > {message}")

    def ask_for_approval(self, context: RequestContext, action: ProposedAction) -> None:
        print(f"\n{'='*40}")
        print(f"[MOCK SLACK] APPROVAL REQUEST")
        print(f"Requester: {context.requester_id}")
        print(f"JIRA: {context.jira_key}")
        print(f"Backend Target: {action.target_id}")
        print(f"Action: {action.summary}")
        print(f"Details: {action.details}")
        print(f"Reasoning: {action.reasoning}")
        print(f"{'='*40}")
        
        if not self.interactive:
            print("[MOCK SLACK] Non-interactive mode: Auto-approving...")
            return
        
        # In a real app, this would wait for a web callback. 
        # For the local tool, we'll let the cli-driver handle the user input.
