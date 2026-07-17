# FILE: product-service/Dockerfile
# PURPOSE: Packages the product-service into a container image for Kubernetes.
#
# WHAT TO BUILD HERE:
#   - Base image: python:3.11-slim
#   - Set WORKDIR /app
#   - COPY requirements.txt and RUN pip install (separate layer for cache efficiency)
#   - COPY main.py
#   - Set default ENV vars: FAILURE_RATE=0.0, VERSION=stable
#   - EXPOSE 8001
#   - CMD: run uvicorn on 0.0.0.0:8001
#
# The canary overlay in k8s/overlays/canary/ will override FAILURE_RATE=0.3
# and VERSION=canary at deploy time via Kubernetes env patches.
