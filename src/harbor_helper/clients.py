"""
Standard clients for JIRA and Harbor.
"""

import requests
from typing import Dict, Any, List
from .models import ProposedAction, ExecutionResult, RequestContext, ActionKind, HarborRegistryConfig


class AtlassianJiraClient:
# ... (rest of Jira client remains same until RealHarborClient)
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


class SingleRegistryHarborClient:
    """Handles interaction with a single Harbor instance."""

    def __init__(self, url: str, user: str, password: str):
        self.url = url.rstrip("/")
        self.auth = (user, password)

    def execute(self, action: ProposedAction) -> ExecutionResult:
        try:
            if action.kind == ActionKind.CREATE_PROJECT:
                return self._create_project(action.payload)
            elif action.kind == ActionKind.CREATE_ROBOT:
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


class MultiRegistryHarborClient:
    """Dispatches actions to the correct Harbor registry based on target_id."""

    def __init__(self, configs: List[HarborRegistryConfig]):
        self.registries = {
            cfg.nickname: SingleRegistryHarborClient(cfg.url, cfg.user, cfg.password)
            for cfg in configs
        }

    def execute(self, action: ProposedAction) -> ExecutionResult:
        client = self.registries.get(action.target_id)
        if not client:
            available = list(self.registries.keys())
            return ExecutionResult(
                success=False,
                data={},
                error=f"Registry '{action.target_id}' not found. Available: {available}",
            )
        return client.execute(action)
