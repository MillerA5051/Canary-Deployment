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

## Production Upgrade — CI Path Filters

- Currently ci.yml rebuilds all three images (api-gateway, product-service, locust) on every push regardless of what changed
- In production each service would have its own job with a path filter:
  ```yaml
  on:
    push:
      branches: [main]
      paths:
        - "api-gateway/**"
  ```
- A change to `locust/locustfile.py` would only trigger the locust build, not api-gateway or product-service
- Faster CI, cheaper build minutes, cleaner image history

---

## Production Upgrade — Grafana Auth

- Currently using `admin/admin` — fine for local Minikube, never acceptable in production
- Real options:
  - **SSO/OAuth** — Grafana integrates with Google, GitHub, Okta, etc. Engineers log in with company credentials
  - **LDAP** — same idea, uses company directory
  - **Grafana Teams + RBAC** — control who can see which dashboards (e.g. only on-call sees canary error rate)
- Garmin would use SSO so engineers authenticate with their Garmin credentials
- Note this tradeoff in the README

---

## Phase 10 — Locust Load Profiles (Overlay Pattern)

- Currently Locust args (`--users=10 --spawn-rate=2`) are hardcoded in `locust-deployment.yaml`
- Add a `k8s/overlays/load-test/` overlay that patches users/spawn-rate up for heavy load testing
- Example: `--users=100 --spawn-rate=10` for stress testing the canary rollback trigger
- Same Kustomize patch pattern as the canary overlay — version controlled, applied with one command

### Other ways to scale Locust on the fly (without an overlay):

**Quick edit (opens live deployment in editor):**
```bash
kubectl edit deployment locust -n canary-app
# change --users and --spawn-rate, save, K8s rolls the pod automatically
```

**One-liner patch:**
```bash
kubectl patch deployment locust -n canary-app --type=json \
  -p='[{"op":"replace","path":"/spec/template/spec/containers/0/args","value":["--host=http://api-gateway:8000","--headless","--users=50","--spawn-rate=5"]}]'
```

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
