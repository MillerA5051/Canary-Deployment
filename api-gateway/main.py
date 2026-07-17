# FILE: api-gateway/main.py
# PURPOSE: The front door of the system. All external traffic hits this service first.

# Request, Response, JSONResponse - fastAPI types needed in the middleware routes
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
# prometheus_client
# counter + histogram are the two metric types well define
# generate_latest + CONTENT_TYPE_LATEST are what /metrics returns
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
# used for graving environmental keys
import os
# random + time - needed for fault injection and latency tracking
import random
import time
# httpx - async http client for proxying to product-service
import httpx

app = FastAPI()

# FAILURE_RATE = String > so we change it to be saved as a float
FAILURE_RATE = float(os.getenv("FAILURE_RATE", "0.0"))
# 
VERSION = os.getenv("VERSION", "stable")
# the address api-gateway used to reach product-service
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8001")

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
SERVICE = "api-gateway"

# middleware
@app.middleware("http")
async def metrics_and_fault_middleware(request: Request, call_next):
    if request.url.path in ("/metrics", "/health"):
        return await call_next(request)
    # captures the timestamp before anything happens
    start = time.time()
    # generates a float between 0.0-0.1 if it falls below FAILURE_RATE the fault fires
    if random.random() < FAILURE_RATE:
        duration = time.time() - start
        endpoint = request.url.path
        REQUEST_COUNT.labels(SERVICE, VERSION, request.method, endpoint, "500").inc()
        REQUEST_LATENCY.labels(SERVICE, VERSION, request.method, endpoint).observe(duration)
        # on a fault metrics are still recorded with status "500" before returning
        return JSONResponse(
            status_code=500,
            content={"error":"injected fault", "service":SERVICE, "version":VERSION},
        )
    response = await call_next(request) # on a normal request, this runs the actual route handler, then metrics are recorded with the real status code
    duration = time.time()-start
    endpoint = request.url.path
    REQUEST_COUNT.labels(SERVICE, VERSION, request.method, endpoint, str(response.status_code)).inc()
    REQUEST_LATENCY.labels(SERVICE, VERSION, request.method, endpoint).observe(duration)
    return response

# routes
# /health - returns a plain dict, kubernetes uses this for liveness/readiness probes
@app.get("/health")
async def health():
    return{"status": "ok", "service": SERVICE, "version": VERSION}

# /metrics 
# - generate_latest() serializes all prometheus counters/histograms into the text format Prometheus scrapes
# - CONTENT_TYPE_LATEST sets the correct content-type header so Prometheus knows how to parse it
@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# products and /product{product_id}
# - async with httpx.AsyncClient, opens a connection, forwards the request to product-service using the PRODUCT_SERVICE_URL env var and passes the response straight back.
# try/except catches connection errors (product-service is down or unreachable) and returns a 503 instead of crashing
@app.get("/products")
async def list_products():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{PRODUCT_SERVICE_URL}/products")
            return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")
        except httpx.RequestError as exc:
            return JSONResponse(status_code=503, content= {"error": "product-service unavailable"})

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
            return Response(content=resp.content, status_code=resp.status_code, media_type="application/json")
        except httpx.RequestError as exc:
            return JSONResponse(status_code=503, content={"error": "product-service unavailable"})
        
        