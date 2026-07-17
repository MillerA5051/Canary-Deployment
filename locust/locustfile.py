# FILE: locust/locustfile.py
# PURPOSE: Defines the load test behavior — what endpoints to hit and how often.
#          Locust uses this to generate continuous traffic against the api-gateway,
#          which drives the Prometheus metrics that the rollback script reads.
#
# WHAT TO WRITE HERE:
#   - Import HttpUser, task, between from locust
#   - class ApiGatewayUser(HttpUser):
#       wait_time = between(0.5, 2)   ← simulates realistic user pacing
#
#       @task(3)                      ← weight 3: hits more often
#       def list_products(self):
#           self.client.get("/products")
#
#       @task(1)
#       def get_product(self):
#           self.client.get("/products/1")   ← or random id 1-5
#
#       @task(1)
#       def health_check(self):
#           self.client.get("/health")
#
# Run locally: locust -f locustfile.py --host http://simulatedfailure.local
