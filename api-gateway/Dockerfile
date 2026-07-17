# FILE: api-gateway/Dockerfile
# PURPOSE: Packages the api-gateway into a container image for Kubernetes.

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
ENV FAILURE_RATE=0.0
ENV VERSION=stable
ENV PRODUCT_SERVICE_URL=http://product-service:8001
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]