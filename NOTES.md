# Project Notes

## Security TODOs (Phase 10 / Polish)

### /metrics endpoint
- Currently exposed through Ingress at path `/` — meaning it's publicly accessible
- In production, `/metrics` should be **cluster-internal only**: Prometheus scrapes it pod-to-pod and it never needs to go through Ingress
- Fix: add an explicit Ingress rule that only routes `/products` (not `/metrics` or `/health`), OR remove those paths from Ingress entirely
- `/health` is only used by K8s liveness/readiness probes — also doesn't need to be public

## Production Upgrade — ServiceMonitors Instead of additionalScrapeConfigs

- Currently using `additionalScrapeConfigs` in `values-prometheus.yaml` — targets are hardcoded centrally
- In production, each service would ship its own `ServiceMonitor` CRD alongside its Deployment
- Prometheus auto-discovers ServiceMonitors cluster-wide — no central config change needed when new services are added
- Tradeoff: additionalScrapeConfigs = simple + centralized. ServiceMonitors = scalable + distributed ownership
- Garmin-scale orgs use ServiceMonitors so teams own their own scrape config
- Worth mentioning this tradeoff in the README

---

## Stretch Goal — Real Bug Instead of Simulated Failure

- Currently `FAILURE_RATE=0.3` synthetically injects 500s to simulate a bad release
- Stretch: deploy an actual buggy version of product-service (e.g. infinite loop, broken DB query, memory leak) as the canary image
- The detection + rollback pipeline would work identically — just organic failures instead of forced ones
- This would make the project closer to a real production canary deployment scenario
- Way down the road, after everything else is working end-to-end

---

### Auth
- Real auth would sit at the **api-gateway layer** (JWT validation before proxying to product-service)
- Common patterns: OAuth2 Proxy sidecar, or api-gateway validates Bearer tokens itself
- nginx basic auth annotations exist but are not production-grade
- For this project: note in README that auth lives at the api-gateway layer — the architecture already supports it since all traffic flows through api-gateway first
