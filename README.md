# Harbor Helper

A Mirantis corporate tool for automated dev-ops operations on Harbor OCI registries.

## Project Methodology

This project is built using a **Spec and Intent-Driven** development approach.
- 🎯 **[INTENT.md](INTENT.md)**: The "North Star" - why we are building this.
- 📋 **[SPEC.md](SPEC.md)**: Requirements, technical constraints, and scope.
- 🤖 **[AI_GUIDELINES.md](AI_GUIDELINES.md)**: Rules of engagement for AI agents.

## Developer Quick Start

### Prerequisites

- `uv` (recommended for dependency management)
- `podman` (preferred for container builds)

### Installation

```bash
# Sync dependencies and create virtual environment
make install-dev
```

### Running Locally (Development and Mocking)

You can run the full agent workflow locally using mocks. This is the preferred way to test LLM interpretations and user interaction flows without needing Harbor, JIRA, or Slack credentials.

```bash
# INTERACTIVE: Follow the full flow, including approval prompt
make run

# DEVELOPER REPL: Communicate with a local LLM in a loop with verbose side-effects (NFR 13)
make repl

# NON-INTERACTIVE: Auto-approve using the stub/mock flow
make run-stub

# TUNABLE: Override the LLM model or URL via environment variables
make run LLM_MODEL=llama3 OLLAMA_URL=http://my-gpu-server:11434/api/chat

# ADVANCED: Directly using the local tool with options
uv run harbor-helper-local "Create a new Harbor robot for the automation team" --user U001 --approver U002
```

The local tool simulations:
- **JIRA**: Increments mock ticket IDs (e.g., `PRODENG-100`).
- **Slack**: Consistently outputs message blocks and threads to the console.
- **Harbor**: Returns successful mock responses for Project and Robot creation.
- **Ollama**: Requires a local Ollama instance running by default.

### Testing

```bash
# Run all tests
make test
```

### Linting and Formatting

```bash
make lint
make format
```

## Building and Distribution

- **Build Wheel**: `make build`
- **OCI Image**: `make image-build` (Uses `harbor_helper.Containerfile`)
- **Push to Dev Registry**: `make image-push-dev`
- **Push to Prod Registry**: `make image-push-prod`

## Kubernetes

Deployment manifests are located in `k8s/`.
```bash
make k8s-apply
```

See [docs/usage.md](docs/usage.md) for end-user documentation and configuration details.
