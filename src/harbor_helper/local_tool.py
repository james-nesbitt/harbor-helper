"""
A tool for running Harbor Helper's logic flow locally with mocked external integrations.
"""

import argparse
import logging
import sys
import uuid
import os
from .app import HarborHelper
from .models import RequestContext, ActionKind, ProposedAction
from .interpreter_ollama import OllamaInterpreter
from .mocks import MockJiraClient, MockHarborClient, MockMessenger
from .clients import AtlassianJiraClient, RealHarborClient
from .slack import SlackMessenger

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run Harbor Helper locally for testing.")
    parser.add_argument("query", help="The raw user request (e.g., 'create project test')")
    parser.add_argument("--jira", help="A pre-existing JIRA ticket key (e.g., PRODENG-123)")
    parser.add_argument("--user", default="U123456", help="The simulated user ID (Slack ID format)")
    parser.add_argument("--channel", default="C123456", help="The simulated channel ID")
    parser.add_argument("--approver", default="U654321", help="The simulated approver ID")
    parser.add_argument("--non-interactive", action="store_true", help="Auto-approve without user input")
    parser.add_argument("--real-api", action="store_true", help="Use real API clients (requires ENV vars)")
    parser.add_argument("--ollama-url", default="http://localhost:11434/api/chat", help="Ollama API base URL")
    parser.add_argument("--model", default="mistral", help="LLM model name")

    args = parser.parse_args()

    # Determine clients based on flag
    if args.real_api:
        logger.info("Using REAL API clients (Harbor, JIRA, Slack)")
        jira = AtlassianJiraClient(
            url=os.getenv("HARBOR_HELPER_JIRA_URL"),
            user=os.getenv("HARBOR_HELPER_JIRA_USER"),
            token=os.getenv("HARBOR_HELPER_JIRA_TOKEN")
        )
        harbor = RealHarborClient(
            url=os.getenv("HARBOR_HELPER_HARBOR_URL"),
            user=os.getenv("HARBOR_HELPER_HARBOR_USER"),
            password=os.getenv("HARBOR_HELPER_HARBOR_PASS")
        )
        messenger = SlackMessenger(bot_token=os.getenv("SLACK_BOT_TOKEN"))
    else:
        logger.info("Using MOCKED API clients for JIRA, Harbor, and Slack")
        jira = MockJiraClient()
        harbor = MockHarborClient()
        messenger = MockMessenger(interactive=not args.non_interactive)

    # Use Ollama for interpretation (this tool's primary goal)
    interpreter = OllamaInterpreter(model=args.model, url=args.ollama_url)

    # Core logic
    helper = HarborHelper(
        interpreter=interpreter,
        jira=jira,
        harbor=harbor,
        messenger=messenger,
        approved_engineers=[args.user, args.approver]
    )

    # Simulate request
    context = RequestContext(
        raw_text=args.query,
        requester_id=args.user,
        channel_id=args.channel,
        thread_ts=str(uuid.uuid4()),
        jira_key=args.jira
    )

    logger.info(f"Processing request: '{args.query}' from {args.user}")
    
    # Run interpretation and approval flow
    # Since this is a CLI tool, we simulate the async Slack lifecycle
    
    # 1. HarborHelper.handle_request initiates interpretation and kicks off the Slack/JIRA flow
    # To run this synchronously in a CLI, we rely on the fact that handle_request calls messenger.ask_for_approval
    # We'll monkeypatch or slightly intercept this for the CLI experience if needed, 
    # but the simplest way is to follow the natural flow.

    # Intercepting the messenger so we can prompt for approval in the same CLI loop
    original_approval = messenger.ask_for_approval
    
    def cli_approval_interceptor(ctx, action):
        original_approval(ctx, action)
        if args.non_interactive:
            choice = 'y'
        else:
            choice = input("\n[CLI] Approve this action? (y/n/exit): ").lower().strip()
        
        if choice == 'y':
            helper.handle_approval(ctx, action, args.approver)
        elif choice == 'n':
            helper.handle_rejection(ctx, action, args.approver)
        else:
            logger.info("Operation cancelled.")
            sys.exit(0)

    # Reconnect the intercepted approval 
    messenger.ask_for_approval = cli_approval_interceptor

    try:
        helper.handle_request(context)
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
