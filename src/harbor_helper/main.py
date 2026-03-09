"""
Main entrypoint for the Harbor Helper service.
"""

import os
import json
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .app import HarborHelper
from .models import RequestContext, ProposedAction, ActionKind
from .interpreter_ollama import OllamaInterpreter
from .clients import AtlassianJiraClient, RealHarborClient
from .slack import SlackMessenger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Load configuration
    approved_engineers = os.getenv("HARBOR_HELPER_APPROVED_ENGINEERS", "").split(",")
    jira_url = os.getenv("HARBOR_HELPER_JIRA_URL")
    jira_user = os.getenv("HARBOR_HELPER_JIRA_USER")
    jira_token = os.getenv("HARBOR_HELPER_JIRA_TOKEN")
    harbor_url = os.getenv("HARBOR_HELPER_HARBOR_URL")
    harbor_user = os.getenv("HARBOR_HELPER_HARBOR_USER")
    harbor_pass = os.getenv("HARBOR_HELPER_HARBOR_PASS")
    slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
    slack_app_token = os.getenv("SLACK_APP_TOKEN")
    model_name = os.getenv("HARBOR_HELPER_MODEL", "mistral")
    ollama_url = os.getenv(
        "HARBOR_HELPER_OLLAMA_URL", "http://localhost:11434/api/chat"
    )

    # Initialize components
    interpreter = OllamaInterpreter(model=model_name, url=ollama_url)
    jira = AtlassianJiraClient(url=jira_url, user=jira_user, token=jira_token)
    harbor = RealHarborClient(url=harbor_url, user=harbor_user, password=harbor_pass)
    messenger = SlackMessenger(bot_token=slack_bot_token)

    helper = HarborHelper(
        interpreter=interpreter,
        jira=jira,
        harbor=harbor,
        messenger=messenger,
        approved_engineers=approved_engineers,
    )

    # Initialize Slack App
    app = App(token=slack_bot_token)

    @app.event("app_mention")
    def handle_mention(event, say):
        text = event["text"]
        jira_key = None
        # Simple JIRA key extractor (PRODENG-123, etc)
        import re

        match = re.search(r"([A-Z]+-\d+)", text)
        if match:
            jira_key = match.group(1)

        context = RequestContext(
            raw_text=text,
            requester_id=event["user"],
            channel_id=event["channel"],
            thread_ts=event.get("thread_ts") or event["ts"],
            jira_key=jira_key,
        )
        helper.handle_request(context)

    @app.action("approve_action")
    def handle_approval_action(ack, body, client):
        ack()
        payload = json.loads(body["actions"][0]["value"])
        approver_id = body["user"]["id"]

        # Reconstruct models from serialized JSON
        context = RequestContext(**payload["context"])

        action_data = payload["action"]
        action_data["kind"] = ActionKind(action_data["kind"])
        action = ProposedAction(**action_data)

        helper.handle_approval(context, action, approver_id)

    @app.action("reject_action")
    def handle_rejection_action(ack, body, client):
        ack()
        payload = json.loads(body["actions"][0]["value"])
        rejecter_id = body["user"]["id"]

        # Reconstruct models from serialized JSON
        context = RequestContext(**payload["context"])

        action_data = payload["action"]
        action_data["kind"] = ActionKind(action_data["kind"])
        action = ProposedAction(**action_data)

        helper.handle_rejection(context, action, rejecter_id)

    # Start Socket Mode handler
    logger.info("Starting Harbor Helper...")
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()


if __name__ == "__main__":
    main()
