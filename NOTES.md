# Project Notes

## Security TODOs (Phase 10 / Polish)

### /metrics endpoint
- Currently exposed through Ingress at path `/` — meaning it's publicly accessible
- In production, `/metrics` should be **cluster-internal only**: Prometheus scrapes it pod-to-pod and it never needs to go through Ingress
- Fix: add an explicit Ingress rule that only routes `/products` (not `/metrics` or `/health`), OR remove those paths from Ingress entirely
- `/health` is only used by K8s liveness/readiness probes — also doesn't need to be public

### Auth
- Real auth would sit at the **api-gateway layer** (JWT validation before proxying to product-service)
- Common patterns: OAuth2 Proxy sidecar, or api-gateway validates Bearer tokens itself
- nginx basic auth annotations exist but are not production-grade
- For this project: note in README that auth lives at the api-gateway layer — the architecture already supports it since all traffic flows through api-gateway first
