# FILE: product-service/main.py
# PURPOSE: Does the actual "work". Returns product data and simulates failures.
# owns the data instead of proxying it

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import os
import random
import time

FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.0"))
VERSION = os.getenv("VERSION", "stable")

SERVICE = "product-service"

app = FastAPI()

#prometheus metrics
# Counter only goes up perfect for request counts
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests", 
    ["service", "version", "method", "endpoint", "status_code"],
)
# Histogram tracks the distribution of values, perfect for latency, can get p50/p95 in grafana for free
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["service", "version", "method", "endpoint"]
)
# note version label on both is the key detail, this is what lets prometheus separate stable from canary traffic in queries

# product catalogue
# product_index is a dict keyed by id, so instead of looping the whole list, you can just do PRODUCT_INDEX.get(3)
PRODUCTS = [
    {"id":1, "name":"GPS Watch Pro", "price": 349.99},
    {"id":2, "name":"Edge 1040 Cycling Computer", "price":599.99},
    {"id":3, "name":"inReach Mini 2", "price": 349.99},
    {"id":4, "name":"Forerunner 965", "price": 599.99},
    {"id":5, "name":"Fenix 7X Solar", "price": 899.99},
]
PRODUCT_INDEX = {p["id"]:p for p in PRODUCTS}

# middleware (same as api-gateway/main.py)
@app.middleware("http")
async def metrics_and_fault_middleware(request: Request, call_next):
    if request.url.path in ("/metrics", "/health"):
        return await call_next(request)
    
    start = time.time()
    
    if random.random() < FAILURE_RATE:
        duration = time.time() - start
        endpoint = request.url.path
        REQUEST_COUNT.labels(SERVICE, VERSION, request.method, endpoint, "500").inc()
        REQUEST_LATENCY.labels(SERVICE, VERSION, request.method, endpoint).observe(duration)
        return JSONResponse(
            status_code=500,
            content={"error": "injected fault", "service": SERVICE, "version": VERSION},
        )
    
    response = await call_next(request)
    duration = time.time()-start
    endpoint = request.url.path
    REQUEST_COUNT.labels(SERVICE, VERSION, request.method, endpoint, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(SERVICE, VERSION, request.method, endpoint).observe(duration)
    return response

# routes
# /health (same as api-gateway/main.py) returns plain dict, k8s uses for liveness/readiness probes
@app.get("/health")
async def health():
    return {"status": "ok", "service": SERVICE, "version": VERSION}

# /metrics (same as api-gateway/main.py) serializes all prometheus counters/histograms into a text format prom. can scrape, and sets the correct content-type header so prom knows how to parse
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# no httpx, no proxying just returns the data directly
@app.get("/products")
async def list_products():
    return {"products": PRODUCTS, "count": len(PRODUCTS), "version": VERSION}

# no httpx, no proxying, returns the data directly. 
# {**product, "version": VERSION} unpacks teh product dict and adds the version field so every response is labeled with which deployment served it.
@app.get("/products/{product_id}")
async def get_product(product_id: int):
    product = PRODUCT_INDEX.get(product_id)
    if not product:
        return JSONResponse(status_code=404, content={"error": f"product {product_id} not found"})
    return {**product, "version": VERSION}