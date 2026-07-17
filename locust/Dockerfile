# FILE: locust/Dockerfile
# PURPOSE: Packages Locust into a container so it can run inside the cluster
#          as a Kubernetes Deployment and generate traffic continuously.
#
# WHAT TO WRITE HERE:
#   - FROM locustio/locust  (official image, no need to install manually)
#   - WORKDIR /mnt/locust
#   - COPY locustfile.py .
#   - EXPOSE 8089  (Locust web UI port)
#   - CMD runs locust headlessly (--headless) with a set number of users
#       e.g. ["locust", "-f", "locustfile.py", "--headless",
#              "-u", "10", "-r", "2",
#              "--host", "http://api-gateway:8000"]
