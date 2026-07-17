# FILE: locust/locustfile.py
# PURPOSE: Defines the load test behavior — what endpoints to hit and how often.
#          Locust uses this to generate continuous traffic against the api-gateway,
#          which drives the Prometheus metrics that the rollback script reads.

# without locust there would be no load, prometheus has nothing to scrape, no requests means no metrics, which means no data in grafana and nothing to trigger the rollback.
from locust import HttpUser, task, between
# HttpUser - base class, each simulated user gets an HTTP client pointed at the target host

class ProductUser(HttpUser):
    # each user waits 1-3 seconds between tasks, simulating realistic think time. (without this every use hammers the service as fast as possible)
    wait_time = between(1,3)
    # @task(3) and @task(1) - number is a weight. list_products runs 3x as often as get_products. so 75% of requests hit /products, 25% hit /products/1
    @task(3)
    def list_products(self):
        self.client.get("/products")

    @task(1)
    def get_product(self):
        self.client.get("/products/1")
