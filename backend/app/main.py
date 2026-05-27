"""
Main FastAPI application.

Entry point for the CloudOps Intelligence backend API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

# Import configuration
from app.config.settings import settings

# Import database
from app.models.database import init_db

# Import routes
from app.routes import health, deployments, incidents

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown logic.
    
    Runs on server start, yields during operation, 
    runs cleanup on shutdown.
    """
    # ===== STARTUP =====
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        # Initialize database
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # ===== SHUTDOWN =====
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered DevOps platform for deployment tracking and incident management",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ===== MIDDLEWARE =====

# CORS (allow requests from frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local dev
        "http://localhost",            # Local
        "http://127.0.0.1",           # Local
        "http://*:3000",              # Any port 3000
        "*"                           # CHANGE THIS IN PRODUCTION
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log HTTP requests and response times."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )
    
    return response


# ===== EXCEPTION HANDLERS =====

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )


# ===== ROUTES =====

# Health check routes
app.include_router(health.router)

# Deployment routes
app.include_router(deployments.router)

# Incident routes
app.include_router(incidents.router)


# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/api/")
def api_root():
    """API root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "endpoints": {
            "health": "/api/health",
            "deployments": "/api/deployments",
            "incidents": "/api/incidents",
            "docs": "/api/docs"
        }
    }


# ===== METRICS (Prometheus) =====

from prometheus_client import Counter, Histogram, generate_latest
import time

# Define metrics
request_count = Counter(
    'cloudops_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'cloudops_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)


@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG
    )
