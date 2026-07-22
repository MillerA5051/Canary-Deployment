# FILE: product-service/Dockerfile
# PURPOSE: Packages the product-service into a container image for Kubernetes.

FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
ENV FAILURE_RATE=0.0
ENV VERSION=stable
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]