# Usage Guide

This document describes how to use Harbor Helper to manage Harbor OCI registries.

## Overview

Harbor Helper listens for requests from approved ops engineers on Slack, interprets them using an AI agent, and uses existing JIRA tickets to track and audit the changes. All changes require peer approval before execution.

## Interacting with the Agent

Currently, the agent is interactable via a CLI stub (Slack integration in progress).

### CLI Usage

```bash
harbor-helper-local "I need a new Harbor project for my team"
```

1. **Interpretation**: The agent will describe the planned change.
2. **Approval**: You will be asked to approve the change.
3. **Execution**: If approved, the agent performs the action.

### Command Line Options

- `--non-interactive`: Automate the approval step with a stub approver (useful for automation/CI).

## Environments and Configuration

The following environment variables can be used to configure the application's behavior:

- `HARBOR_HELPER_APPROVED_ENGINEERS`: Comma-separated list of approved engineer IDs.
- `HARBOR_HELPER_HARBOR_URL`: The URL of the Harbor registry.
- `JIRA_PROJECT`: Defaults to `PRODENG`.

## Workflow Policies

- **Peer Review**: By default, the person requesting a change cannot be the one to approve it.
- **JIRA Integration**: Every request must be tied to an existing `PRODENG` or `IT` JIRA ticket. If no ticket ID is provided in the request, or if the ticket belongs to another project, the request will be rejected.
- **Credentials**: Robot tokens are never posted in public channels. They are sent via Direct Message (DM) to the requester.
