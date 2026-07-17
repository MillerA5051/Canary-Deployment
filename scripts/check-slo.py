# FILE: scripts/check-slo.py
# PURPOSE: Queries Prometheus and checks whether the canary error rate exceeds the SLO.
#          Exits with code 1 if the SLO is breached, which triggers rollback.yml.
#
# WHAT TO BUILD HERE:
#   - Read PROMETHEUS_URL from env (default http://localhost:9090)
#   - Read ERROR_THRESHOLD from env (default 0.05 = 5%)
#   - Query Prometheus instant API with a PromQL expression like:
#       sum(rate(http_requests_total{version="canary", status_code=~"5.."}[5m]))
#       /
#       sum(rate(http_requests_total{version="canary"}[5m]))
#   - If result > ERROR_THRESHOLD:
#       print the error rate and a BREACH message
#       sys.exit(1)   ← GitHub Actions sees this as failure and triggers rollback
#   - Else:
#       print the error rate and an OK message
#       sys.exit(0)
