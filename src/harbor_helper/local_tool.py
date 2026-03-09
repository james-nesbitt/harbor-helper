"""
A tool for running Harbor Helper's logic flow locally with mocked external integrations.
"""

import argparse
import logging
import sys
import uuid
import os
from .app import HarborHelper
from .models import RequestContext, ActionKind, ProposedAction, HarborRegistryConfig
from .interpreter_ollama import OllamaInterpreter
from .mocks import MockJiraClient, MockHarborClient, MockMessenger
from .clients import AtlassianJiraClient, MultiRegistryHarborClient
from .slack import SlackMessenger

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run Harbor Helper locally for testing.")
    parser.add_argument("query", nargs='?', help="The raw user request (e.g., 'create project test')")
    parser.add_argument("--jira", help="A pre-existing JIRA ticket key (e.g., PRODENG-123)")
    parser.add_argument("--user", default="U123456", help="The simulated user ID (Slack ID format)")
    parser.add_argument("--channel", default="C123456", help="The simulated channel ID")
    parser.add_argument("--approver", default="U654321", help="The simulated approver ID")
    parser.add_argument("--non-interactive", action="store_true", help="Auto-approve without user input")
    parser.add_argument("--real-api", action="store_true", help="Use real API clients (requires ENV vars)")
    parser.add_argument("--ollama-url", default="http://localhost:11434/api/chat", help="Ollama API base URL")
    parser.add_argument("--model", default="mistral", help="LLM model name")
    parser.add_argument("--verbose", action="store_true", help="Display LLM prompt, response, and side-effects")
    parser.add_argument("--repl", action="store_true", help="Run in interactive REPL mode")
    parser.add_argument("--registry", action="append", help="Harbor registry config (nickname:url:user:pass)")
    parser.add_argument("--existing-project", action="append", help="Simulate existing project in mocks")
    parser.add_argument("--existing-robot", action="append", help="Simulate existing robot in mocks")

    args = parser.parse_args()

    if not args.repl and not args.query:
        parser.error("Either 'query' or '--repl' is required.")

    # Parse registries
    registry_configs = []
    if args.registry:
        for reg_str in args.registry:
            parts = reg_str.split(":", 3)
            if len(parts) == 4:
                registry_configs.append(HarborRegistryConfig(
                    nickname=parts[0], url=parts[1], user=parts[2], password=parts[3]
                ))
    
    # Fallback to dev/prod mocks if none provided
    if not registry_configs:
        registry_configs = [
            HarborRegistryConfig("dev", "http://dev-harbor", "admin", "pass"),
            HarborRegistryConfig("prod", "http://prod-harbor", "admin", "pass"),
        ]

    # Determine clients based on flag
    if args.real_api:
        logger.info("Using REAL API clients (Harbor, JIRA, Slack)")
        jira = AtlassianJiraClient(
            url=os.getenv("HARBOR_HELPER_JIRA_URL"),
            user=os.getenv("HARBOR_HELPER_JIRA_USER"),
            token=os.getenv("HARBOR_HELPER_JIRA_TOKEN")
        )
        harbor = MultiRegistryHarborClient(registry_configs)
        messenger = SlackMessenger(bot_token=os.getenv("SLACK_BOT_TOKEN"))
    else:
        logger.info("Using MOCKED API clients for JIRA, Harbor, and Slack")
        jira = MockJiraClient()
        harbor = MockHarborClient(
            existing_projects=args.existing_project,
            existing_robots=args.existing_robot
        )
        messenger = MockMessenger(interactive=not args.non_interactive)

    # Use Ollama for interpretation
    interpreter = OllamaInterpreter(
        model=args.model, 
        url=args.ollama_url, 
        available_targets=[cfg.nickname for cfg in registry_configs],
        verbose=args.verbose
    )

    # Core logic
    helper = HarborHelper(
        interpreter=interpreter,
        jira=jira,
        harbor=harbor,
        messenger=messenger,
        approved_engineers=[args.user, args.approver]
    )

    def process_query(query, jira_key):
        # Simulate request
        context = RequestContext(
            raw_text=query,
            requester_id=args.user,
            channel_id=args.channel,
            thread_ts=str(uuid.uuid4()),
            jira_key=jira_key
        )

        logger.info(f"Processing request: '{query}' from {args.user}")
        
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
                # We don't exit here if in REPL mode
                if not args.repl:
                    sys.exit(0)

        # Reconnect the intercepted approval 
        messenger.ask_for_approval = cli_approval_interceptor

        try:
            helper.handle_request(context)
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            if not args.repl:
                sys.exit(1)

    if args.repl:
        logger.info("Starting Harbor Helper REPL. Type 'exit' or use Ctrl+C to quit.")
        while True:
            try:
                query = input("\n[REPL] Request > ").strip()
                if query.lower() in ["exit", "quit"]:
                    break
                if not query:
                    continue
                jira_key = input("[REPL] JIRA Ticket (optional) > ").strip() or args.jira
                process_query(query, jira_key)
            except KeyboardInterrupt:
                break
        logger.info("Exiting REPL.")
    else:
        process_query(args.query, args.jira)

if __name__ == "__main__":
    main()
