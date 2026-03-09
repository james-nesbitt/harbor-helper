# Packaging for Kubernetes (SPEC §6). Multi-stage build using uv.

FROM ghcr.io/astral-sh/uv:python3.12-slim AS builder
WORKDIR /build

# Build wheel only; no dev deps in final image
COPY pyproject.toml .
COPY src/ src/
RUN uv build --wheel --out-dir dist/

FROM python:3.12-slim AS runtime
WORKDIR /app

# Non-root user (good practice for K8s)
RUN adduser --disabled-password --gecos "" appuser

# Install wheel from builder (no build tools in runtime)
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

USER appuser

# Default: run CLI. Override in Deployment when using a long-running listener (e.g. Slack).
ENTRYPOINT ["harbor-helper"]
