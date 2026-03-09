# Kubernetes packaging and distribution (SPEC §6)

- **configmap.yaml** – Non-sensitive app config (e.g. `HARBOR_HELPER_HARBOR_URL`).
- **deployment.yaml** – Deployment for harbor-helper. Uses a placeholder `sleep infinity` so the pod stays up until a long-running listener (e.g. Slack) is the entrypoint.

## OCI artifact registries (SPEC §6)

OCI artifacts (container images) must be pushed to:

- **Dev:** `oci://registry.ci.mirantis.com/jnesbitt/` → use `make image-push-dev`
- **Production:** `registry.mirantis.com/jnesbitt/` → use `make image-push-prod`

**Podman** is the preferred tool for building OCI images (`CONTAINER_CLI=podman` by default; set to `docker` if needed).

## Prerequisites

- Container image built and available to the cluster (e.g. `make image-build` then `make image-push-dev` or `make image-push-prod`). Builds use podman by default.
- Create a Secret for sensitive env (approved engineers list, API tokens) and reference it in the Deployment `envFrom` (uncomment `secretRef` and create `harbor-helper-secrets`).

## Apply manifests

```bash
kubectl apply -f k8s/
```

Default deployment image is `registry.ci.mirantis.com/jnesbitt/harbor-helper:0.1.0` (dev). For production, use `registry.mirantis.com/jnesbitt/harbor-helper:0.1.0`.

## Building and pushing the image

```bash
make image-build        # uses podman by default (CONTAINER_CLI=podman)
make image-push-dev     # push to registry.ci.mirantis.com/jnesbitt/ (dev)
make image-push-prod    # push to registry.mirantis.com/jnesbitt/ (production)
```
