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

### Running Locally (Development)

```bash
# Run the CLI with a stub request
uv run python -m harbor_helper "I need a new Harbor project"

# Run non-interactive for testing
make run-stub
```

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
