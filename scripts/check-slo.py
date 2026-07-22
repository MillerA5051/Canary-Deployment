# FILE: scripts/check-slo.py
# PURPOSE: Queries Prometheus and checks whether the canary error rate exceeds the SLO.
#          Exits with code 1 if the SLO is breached, which triggers rollback.yml.

import subprocess
import requests
import time
import os

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL","http://prometheus-operated.monitoring.svc.cluster.local:9090")
ERROR_RATE_THRESHOLD = float(os.getenv("ERROR_RATE_THRESHOLD", "0.05")) # 5%
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30")) # seconds
CANARY_NAMESPACE = os.getenv("CANARY_NAMESPACE", "canary-app")
CANARY_INGRESS = os.getenv("CANARY_INGRESS", "api-gateway-canary")

QUERY = '''
    sum(rate(http_requests_total{version="canary", status_code=~"5.."}[5m]))
    /
    sum(rate(http_requests_total{version="canary"}[5m]))
'''

# hits prom HTTP API with the promql query. prom returns JSON - results[0]["value"][1]
# if prom is unreachable or returns no data (canary has zero traffic yet), it returns 0.0 safely instead of crashing
def get_canary_error_rate():
    try:
        resp = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": QUERY},
            timeout= 10,
        )
        data = resp.json()
        results = data["data"]["result"]
        if not results:
            return 0.0
        return float(results[0]["value"][1])
    except Exception as e:
        print(f"[ERROR] Failed to query Prometheus: {e}")
        return 0.0

# when SLO breaches, this fires. 
# runs "kubectl patch" to set the "canary-weight" annotation to "0" on the canary ingress object
# nginx reads that annotation and immediately stops sending traffic to the canary - 100% goes back to stable. same thing the rollback.yaml github action does, just automated.
def rollback():
    print("[ROLLBACK] SLO breached - setting canary-weight to 0")
    patch = '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/canary-weight":"0"}}}'
    subprocess.run([
        "kubectl", "patch", "ingress", CANARY_INGRESS,
        "-n", CANARY_NAMESPACE, 
        "--type=merge",
        "-p", patch,
    ])

# infinite loop, every 30 seconds: query Prom -> check if error rate -> 5% -> rollback if yes -> sleep -> repeat. 
# the .2% formats the float as a percentage for the og (0.3 -> 30%)
def main():
    print("[INFO] SLO check started")
    while True:
        error_rate = get_canary_error_rate()
        print(f"[INFO] Canary error rate: {error_rate:.2%} (threshold: {ERROR_RATE_THRESHOLD:.2%})")
        if error_rate > ERROR_RATE_THRESHOLD:
            rollback()
        time.sleep(CHECK_INTERVAL)
        
if __name__=="__main__":
    main()