# Tooling for build, test, and distribution (NFR 5) using uv for environment control

.PHONY: install install-dev test run run-stub build clean image-build image-push image-push-dev image-push-prod k8s-apply k8s-delete lint format

install:
	uv sync

install-dev:
	uv sync --all-extras

test:
	uv run pytest tests/ -v --cov=src/harbor_helper --cov-report=term-missing

test-all:
	uv run pytest tests/ -v --run-ollama --cov=src/harbor_helper --cov-report=term-missing

lint:
	uv run ruff check .

format:
	uv run ruff format .

# --- Local development configuration ---
OLLAMA_URL ?= http://localhost:11434/api/chat
LLM_MODEL ?= mistral

run:
	uv run harbor-helper-local --ollama-url $(OLLAMA_URL) --model $(LLM_MODEL) "I need a new Harbor project"

# Non-interactive run (local tool)
run-stub:
	uv run harbor-helper-local --non-interactive --ollama-url $(OLLAMA_URL) --model $(LLM_MODEL) "create a new robot account"

# Interactive developer REPL (Requirement 13)
repl:
	uv run harbor-helper-local --repl --verbose --ollama-url $(OLLAMA_URL) --model $(LLM_MODEL)

build:
	uv build

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/ .uv/

# --- Kubernetes packaging and distribution (SPEC §6) ---
# Podman is the preferred tool for OCI image building. OCI paths: dev = .../jnesbitt/, prod = .../jnesbitt/
CONTAINER_CLI ?= podman
IMAGE ?= harbor-helper:0.1.0
REGISTRY ?= ""
DEV_REGISTRY ?= registry.ci.mirantis.com/jnesbitt
PROD_REGISTRY ?= registry.mirantis.com/jnesbitt

image-build:
	$(CONTAINER_CLI) build -f harbor_helper.Containerfile -t $(IMAGE) .

image-push: image-build
	@if [ -z "$(REGISTRY)" ]; then echo "Set REGISTRY=... or use make image-push-dev / make image-push-prod"; exit 1; fi
	$(CONTAINER_CLI) tag $(IMAGE) $(REGISTRY)/$(IMAGE)
	$(CONTAINER_CLI) push $(REGISTRY)/$(IMAGE)

# Push OCI image to dev registry (SPEC §6: oci://registry.ci.mirantis.com/jnesbitt/)
image-push-dev: image-build
	$(CONTAINER_CLI) tag $(IMAGE) $(DEV_REGISTRY)/$(IMAGE)
	$(CONTAINER_CLI) push $(DEV_REGISTRY)/$(IMAGE)

# Push OCI image to production registry (SPEC §6: registry.mirantis.com/jnesbitt/)
image-push-prod: image-build
	$(CONTAINER_CLI) tag $(IMAGE) $(PROD_REGISTRY)/$(IMAGE)
	$(CONTAINER_CLI) push $(PROD_REGISTRY)/$(IMAGE)

k8s-apply:
	kubectl apply -f k8s/

k8s-delete:
	kubectl delete -f k8s/ --ignore-not-found
