"""
Slack integration using Bolt.
"""

import json
from slack_bolt import App
from .models import RequestContext, ProposedAction


class SlackMessenger:
    def __init__(self, bot_token: str):
        self.client = App(token=bot_token).client

    def reply(self, context: RequestContext, message: str):
        self.client.chat_postMessage(
            channel=context.channel_id, thread_ts=context.thread_ts, text=message
        )

    def send_dm(self, user_id: str, message: str):
        self.client.chat_postMessage(channel=user_id, text=message)

    def ask_for_approval(self, context: RequestContext, action: ProposedAction):
        # Serialize essential data to a format that fits in Slack action 'value'
        # Slack value limit is 2000 chars. Let's hope JSON ProposedAction fits.
        # Otherwise we'd need a backend store (like JIRA or a DB).
        payload = json.dumps(
            {
                "action": {
                    "kind": action.kind,
                    "summary": action.summary,
                    "details": action.details,
                    "reasoning": action.reasoning,
                    "payload": action.payload,
                },
                "context": {
                    "raw_text": context.raw_text,
                    "requester_id": context.requester_id,
                    "channel_id": context.channel_id,
                    "thread_ts": context.thread_ts,
                    "jira_key": context.jira_key,
                },
            }
        )

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"I've interpreted a request from <@{context.requester_id}>. JIRA: *{context.jira_key}*\n"
                    f"*Action*: {action.summary}\n"
                    f"*Details*: {action.details}\n\n"
                    "Please have a peer approve this.",
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "action_id": "approve_action",
                        "value": payload,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "action_id": "reject_action",
                        "value": payload,
                    },
                ],
            },
        ]
        self.client.chat_postMessage(
            channel=context.channel_id,
            thread_ts=context.thread_ts,
            blocks=blocks,
            text=f"Approval request for {action.summary}",
        )
