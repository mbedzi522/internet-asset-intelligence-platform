
from fastapi import FastAPI, Depends, HTTPException, status, Request
from starlette.responses import Response
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import json
import os
import logging
import time
from typing import List, Optional
from opensearchpy import OpenSearch
from prometheus_client import generate_latest, Counter, Histogram, Gauge

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'api_requests_total', 'Total API Requests',
    ['endpoint', 'method', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds', 'API Request Latency',
    ['endpoint', 'method']
)
OPENSEARCH_QUERY_LATENCY = Histogram(
    'opensearch_query_duration_seconds', 'OpenSearch Query Latency',
    ['endpoint']
)
ACTIVE_REQUESTS = Gauge(
    'api_active_requests', 'Number of active API requests',
    ['endpoint', 'method']
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_ipaddr
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_ipaddr, default_limits=["100/minute"])
app = FastAPI(
    title="Internet Asset Intelligence API",
    description="API for searching and managing internet asset data, a Shodan competitor.",
    version="0.1.0",
)
app.state.limiter = limiter
app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# --- Configuration ---
class Config:
    def __init__(self):
        self.opensearch_host = os.getenv("OPENSEARCH_HOST", "localhost")
        self.opensearch_port = int(os.getenv("OPENSEARCH_PORT", "9200"))
        self.opensearch_user = os.getenv("OPENSEARCH_USER", "admin")
        self.opensearch_password = os.getenv("OPENSEARCH_PASSWORD", "admin")
        self.opensearch_index_prefix = os.getenv("OPENSEARCH_INDEX_PREFIX", "asset-intelligence-")
        # Placeholder for JWT secret, audience, etc.
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "super-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")

config = Config()

# --- OpenSearch Client ---
def get_opensearch_client():
    client = OpenSearch(
        hosts=[{'host': config.opensearch_host, 'port': config.opensearch_port}],
        http_auth=(config.opensearch_user, config.opensearch_password),
        use_ssl=True,
        verify_certs=False, # Set to True in production with proper CA certs
        ssl_assert_hostname=False,
        ssl_show_warn=False
    )
    if not client.ping():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="OpenSearch is not available")
    return client

# --- Auth (Placeholder) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # In a real application, this would decode and validate the JWT token
    # and fetch user roles/permissions from a database.
    # For now, a dummy user.
    if token == "dummy_admin_token":
        return {"username": "admin", "roles": ["admin", "user"]}
    elif token == "dummy_user_token":
        return {"username": "user", "roles": ["user"]}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if "admin" not in current_user["roles"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

# --- Models ---
class SearchQuery(BaseModel):
    query: str
    page: int = 1
    size: int = 10

class DeviceDetail(BaseModel):
    id: str
    timestamp: str
    ip: str
    port: int
    protocol: str
    probes: dict
    enrichment: dict
    risk_score: int
    risk_breakdown: dict

# --- Endpoints ---
@app.get("/", tags=["Healthcheck"])
async def root():
    return {"message": "Internet Asset Intelligence API is running!"}

@app.get("/health", tags=["Healthcheck"])
async def health_check(os_client: OpenSearch = Depends(get_opensearch_client)):
    return {"status": "ok", "opensearch_status": os_client.ping()}

@app.post("/search", response_model=List[DeviceDetail], tags=["Search"])
@limiter.limit("10/minute")
async def search_assets(request: Request, search_query: SearchQuery, current_user: dict = Depends(get_current_user), os_client: OpenSearch = Depends(get_opensearch_client)):
    start_time = time.time()
    ACTIVE_REQUESTS.labels(endpoint='/search', method='POST').inc()
    try:
        logging.info(f"User {current_user['username']} searching for: {search_query.query}")
    
    # Basic OpenSearch query (needs more sophisticated query building)
    search_body = {
        "query": {
            "multi_match": {
                "query": search_query.query,
                "fields": ["ip", "target.ip", "probes.*", "enrichment.*", "_all"]
            }
        },
        "from": (search_query.page - 1) * search_query.size,
        "size": search_query.size
    }

    try:
        os_start_time = time.time()
        # Search across all relevant indices (e.g., asset-intelligence-*)
        res = os_client.search(index=f"{config.opensearch_index_prefix}*", body=search_body)
        OPENSEARCH_QUERY_LATENCY.labels(endpoint='/search').observe(time.time() - os_start_time)
        hits = res["hits"]["hits"]
        results = []
        for hit in hits:
            source = hit["_source"]
            results.append(DeviceDetail(
                id=source.get("id"),
                timestamp=source.get("timestamp"),
                ip=source.get("target", {}).get("ip"),
                port=source.get("target", {}).get("port"),
                protocol=source.get("target", {}).get("protocol"),
                probes=source.get("probes", {}),
                enrichment=source.get("enrichment", {}),
                risk_score=source.get("risk_score", 0),
                risk_breakdown=source.get("risk_breakdown", {})
            ))
        return results
    except Exception as e:
        logging.error(f"Error during OpenSearch search: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error performing search")
    finally:
        REQUEST_LATENCY.labels(endpoint='/search', method='POST').observe(time.time() - start_time)
        REQUEST_COUNT.labels(endpoint='/search', method='POST', status_code=200).inc() # Assuming success here, more complex handling needed for real status codes
        ACTIVE_REQUESTS.labels(endpoint='/search', method='POST').dec()

@app.get("/device/{device_id}", response_model=DeviceDetail, tags=["Device Details"])
@limiter.limit("30/minute")
async def get_device_details(request: Request, device_id: str, current_user: dict = Depends(get_current_user), os_client: OpenSearch = Depends(get_opensearch_client)):
    start_time = time.time()
    ACTIVE_REQUESTS.labels(endpoint='/device/{device_id}', method='GET').inc()
    try:
        logging.info(f"User {current_user['username']} requesting device details for: {device_id}")
    
    search_body = {
        "query": {
            "term": {
                "id.keyword": device_id
            }
        }
    }

    try:
        res = os_client.search(index=f"{config.opensearch_index_prefix}*", body=search_body)
        hits = res["hits"]["hits"]
        if not hits:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
        
        source = hits[0]["_source"]
        return DeviceDetail(
            id=source.get("id"),
            timestamp=source.get("timestamp"),
            ip=source.get("target", {}).get("ip"),
            port=source.get("target", {}).get("port"),
            protocol=source.get("target", {}).get("protocol"),
            probes=source.get("probes", {}),
            enrichment=source.get("enrichment", {}),
            risk_score=source.get("risk_score", 0),
            risk_breakdown=source.get("risk_breakdown", {})
        )
    except Exception as e:
        logging.error(f"Error fetching device details: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching device details")
    finally:
        REQUEST_LATENCY.labels(endpoint='/device/{device_id}', method='GET').observe(time.time() - start_time)
        REQUEST_COUNT.labels(endpoint='/device/{device_id}', method='GET', status_code=200).inc() # Assuming success here
        ACTIVE_REQUESTS.labels(endpoint='/device/{device_id}', method='GET').dec()

@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    return Response(content=generate_latest().decode("utf-8"), media_type="text/plain")

# --- Admin Endpoints (Placeholder) ---
@app.post("/admin/consent", tags=["Admin"])
async def admin_consent(data: dict, current_admin: dict = Depends(get_current_admin_user)):
    logging.info(f"Admin {current_admin['username']} updating consent: {data}")
    # Logic to update consent tokens, POA documents, etc.
    return {"message": "Consent updated successfully (placeholder)"}

@app.get("/admin/collectors", tags=["Admin"])
async def list_collectors(current_admin: dict = Depends(get_current_admin_user)):
    logging.info(f"Admin {current_admin['username']} listing collectors")
    # Logic to list and manage collector agents
    return [{"id": "collector-001", "status": "active", "last_checkin": "..."}]

# Add more admin endpoints as required (POA upload, job scheduling, etc.)

