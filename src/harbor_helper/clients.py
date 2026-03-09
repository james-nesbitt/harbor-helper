"""
Standard clients for JIRA and Harbor.
"""

import requests
from typing import Dict, Any
from .models import ProposedAction, ExecutionResult, RequestContext


class AtlassianJiraClient:
    def __init__(self, url: str, user: str, token: str, project_key: str = "PRODENG"):
        self.url = url.rstrip("/")
        self.auth = (user, token)
        self.project_key = project_key

    def create_ticket(self, context: RequestContext) -> str:
        # If context already has a jira_key (provided by user), use it.
        # HarborHelper has already validated that it starts with PRODENG-.
        if context.jira_key:
            return context.jira_key

        resp = requests.post(
            f"{self.url}/rest/api/2/issue",
            auth=self.auth,
            json={
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": f"Harbor Request from {context.requester_id}",
                    "description": f"Original Request: {context.raw_text}",
                    "issuetype": {"name": "Task"},
                }
            },
        )
        resp.raise_for_status()
        return resp.json()["key"]

    def add_comment(self, ticket_key: str, comment: str):
        requests.post(
            f"{self.url}/rest/api/2/issue/{ticket_key}/comment",
            auth=self.auth,
            json={"body": comment},
        ).raise_for_status()

    def update_status(self, ticket_key: str, status: str):
        # In a real environment, status name -> transition ID mapping is needed.
        # This implementation logs the transition if mapping is unavailable.
        self.add_comment(ticket_key, f"Workflow Transition: {status}")


class RealHarborClient:
    def __init__(self, url: str, user: str, password: str):
        self.url = url.rstrip("/")
        self.auth = (user, password)

    def execute(self, action: ProposedAction) -> ExecutionResult:
        try:
            if action.kind == "harbor-manage-projects":
                return self._create_project(action.payload)
            elif action.kind == "harbor-new-robot":
                return self._create_robot(action.payload)
            return ExecutionResult(
                success=False, data={}, error=f"Unknown kind {action.kind}"
            )
        except Exception as e:
            return ExecutionResult(success=False, data={}, error=str(e))

    def _create_project(self, payload: Dict[str, Any]) -> ExecutionResult:
        resp = requests.post(
            f"{self.url}/api/v2.0/projects", auth=self.auth, json=payload
        )
        if resp.status_code == 201:
            return ExecutionResult(
                success=True, data={"location": resp.headers.get("Location")}
            )
        return ExecutionResult(success=False, data={}, error=resp.text)

    def _create_robot(self, payload: Dict[str, Any]) -> ExecutionResult:
        resp = requests.post(
            f"{self.url}/api/v2.0/robots", auth=self.auth, json=payload
        )
        if resp.status_code == 201:
            return ExecutionResult(success=True, data=resp.json())
        return ExecutionResult(success=False, data={}, error=resp.text)
