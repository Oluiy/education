"""
EduNerve API Gateway
Central entry point for all microservices with rate limiting, load balancing, and security
"""

from fastapi import FastAPI, Request, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
import httpx
import redis
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import websockets
from fastapi import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Redis for rate limiting
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    default_limits=[f"{os.getenv('RATE_LIMIT_REQUESTS', 100)}/{os.getenv('RATE_LIMIT_WINDOW', 60)}seconds"]
)

# Security
security = HTTPBearer(auto_error=False)

# Prometheus metrics
REQUEST_COUNT = Counter('gateway_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('gateway_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('gateway_active_connections', 'Active connections')

# Service URLs
SERVICE_URLS = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
    "content": os.getenv("CONTENT_SERVICE_URL", "http://localhost:8002"),
    "files": os.getenv("FILE_STORAGE_SERVICE_URL", "http://localhost:8003"),
    "sync": os.getenv("SYNC_MESSAGING_SERVICE_URL", "http://localhost:8004"),
    "assistant": os.getenv("ASSISTANT_SERVICE_URL", "http://localhost:8005"),
    "admin": os.getenv("ADMIN_SERVICE_URL", "http://localhost:8006"),
    "notifications": os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8007")
}

# Circuit breaker configuration
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")),
    "recovery_timeout": int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", "60")),
    "expected_exception": Exception
}

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, set] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        logger.info(f"User {user_id} connected with connection {connection_id}")
    
    def disconnect(self, user_id: str, connection_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        logger.info(f"User {user_id} disconnected connection {connection_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                if connection_id in self.active_connections:
                    try:
                        await self.active_connections[connection_id].send_text(message)
                    except:
                        self.disconnect(user_id, connection_id)
    
    async def broadcast(self, message: str):
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Custom middleware for request logging and metrics
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to headers
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Update metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(duration)
        
        return response

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 API Gateway starting up...")
    
    # Test Redis connection
    try:
        redis_client.ping()
        logger.info("✅ Redis connection successful")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
    
    # Test service connections
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICE_URLS.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                if response.status_code == 200:
                    logger.info(f"✅ {service_name} service healthy")
                else:
                    logger.warning(f"⚠️ {service_name} service unhealthy: {response.status_code}")
            except Exception as e:
                logger.error(f"❌ {service_name} service unavailable: {e}")
    
    yield
    
    logger.info("🛑 API Gateway shutting down...")

# Create FastAPI app
app = FastAPI(
    title="EduNerve API Gateway",
    description="Central API Gateway for EduNerve Educational Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)
app.add_middleware(SlowAPIMiddleware)

# Rate limiting error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user from JWT token"""
    if not credentials:
        return None
    
    try:
        # Forward token to auth service for validation
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SERVICE_URLS['auth']}/api/v1/auth/me",
                headers={"Authorization": f"Bearer {credentials.credentials}"},
                timeout=5.0
            )
            if response.status_code == 200:
                return response.json()
            return None
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

# Circuit breaker for service calls
@circuit(**CIRCUIT_BREAKER_CONFIG)
async def call_service(service_name: str, path: str, method: str = "GET", 
                      headers: Dict = None, json_data: Any = None,
                      params: Dict = None, timeout: float = 30.0):
    """Make a call to a microservice with circuit breaker"""
    service_url = SERVICE_URLS.get(service_name)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    url = f"{service_url}{path}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params,
                timeout=timeout
            )
            return response
        except httpx.TimeoutException:
            logger.error(f"Timeout calling {service_name} at {url}")
            raise HTTPException(status_code=504, detail="Service timeout")
        except httpx.ConnectError:
            logger.error(f"Connection error calling {service_name} at {url}")
            raise HTTPException(status_code=503, detail="Service unavailable")
        except Exception as e:
            logger.error(f"Error calling {service_name}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": list(SERVICE_URLS.keys())
    }

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication"""
    connection_id = str(uuid.uuid4())
    await manager.connect(websocket, user_id, connection_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Forward message to sync service
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{SERVICE_URLS['sync']}/api/v1/sync/messages",
                        json=message_data,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        # Broadcast to relevant users
                        response_data = response.json()
                        await manager.send_personal_message(
                            json.dumps(response_data),
                            user_id
                        )
            except Exception as e:
                logger.error(f"Error forwarding WebSocket message: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(user_id, connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(user_id, connection_id)

# Generic API proxy endpoint
@app.api_route("/api/v1/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@limiter.limit("100/minute")
async def proxy_to_service(
    request: Request,
    service_name: str,
    path: str,
    current_user: Dict = Depends(get_current_user)
):
    """Proxy requests to appropriate microservice"""
    
    # Extract request details
    method = request.method
    headers = dict(request.headers)
    query_params = dict(request.query_params)
    
    # Add user info to headers if authenticated
    if current_user:
        headers["X-User-ID"] = str(current_user.get("id", ""))
        headers["X-User-Role"] = current_user.get("role", "")
        headers["X-School-ID"] = str(current_user.get("school_id", ""))
    
    # Remove host header to avoid conflicts
    headers.pop("host", None)
    
    # Get request body for POST/PUT/PATCH requests
    json_data = None
    if method in ["POST", "PUT", "PATCH"]:
        try:
            json_data = await request.json()
        except:
            pass
    
    # Call the service
    try:
        response = await call_service(
            service_name=service_name,
            path=f"/api/v1/{service_name}/{path}",
            method=method,
            headers=headers,
            json_data=json_data,
            params=query_params
        )
        
        # Return response
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.content else None,
            headers=dict(response.headers)
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in proxy: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Service-specific routes for better organization
@app.get("/api/v1/services")
async def get_services():
    """Get list of available services"""
    services = []
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICE_URLS.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                status = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                status = "unavailable"
            
            services.append({
                "name": service_name,
                "url": service_url,
                "status": status
            })
    
    return {
        "services": services,
        "total": len(services)
    }

# Auth-specific routes
@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    """Login endpoint with rate limiting"""
    json_data = await request.json()
    
    try:
        response = await call_service(
            service_name="auth",
            path="/api/v1/auth/login",
            method="POST",
            json_data=json_data
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/api/v1/auth/register")
@limiter.limit("3/minute")
async def register(request: Request):
    """Registration endpoint with rate limiting"""
    json_data = await request.json()
    
    try:
        response = await call_service(
            service_name="auth",
            path="/api/v1/auth/register",
            method="POST",
            json_data=json_data
        )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

# File upload proxy with special handling
@app.post("/api/v1/files/upload")
async def upload_file(request: Request, current_user: Dict = Depends(get_current_user)):
    """File upload with authentication"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Get the uploaded file
    form = await request.form()
    
    # Forward to file service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICE_URLS['files']}/api/v1/files/upload",
                files={"file": (form["file"].filename, form["file"].file, form["file"].content_type)},
                headers={
                    "X-User-ID": str(current_user["id"]),
                    "X-School-ID": str(current_user["school_id"])
                },
                timeout=60.0
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": request.url.path
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
