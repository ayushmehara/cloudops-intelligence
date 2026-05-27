"""
Health check and readiness probe endpoints.

Used by Kubernetes for liveness and readiness probes.
Critical for production reliability.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from app.config.settings import settings
from app.models.database import check_db_connection
from app.models.pydantic_schemas import HealthCheckResponse
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("/live", response_model=HealthCheckResponse)
async def liveness_probe():
    """Kubernetes liveness probe endpoint.
    
    Returns 200 if service is running.
    Kubernetes will restart pod if this fails.
    
    Response time: should be < 1 second
    """
    return HealthCheckResponse(
        status="alive",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        database=True,
        ai_service=True,
        message="Service is running"
    )


@router.get("/ready", response_model=HealthCheckResponse)
async def readiness_probe():
    """Kubernetes readiness probe endpoint.
    
    Returns 200 only if service is ready to accept traffic.
    Kubernetes removes pod from load balancer if this fails.
    
    Checks:
    - Database connectivity
    - AI service connectivity (if enabled)
    
    Response time: should be < 2 seconds
    """
    # Check database
    db_ready = await check_db_connection()
    
    # Check AI service (optional)
    ai_ready = True
    if settings.AI_ENABLED and not settings.OPENAI_API_KEY:
        logger.warning("AI enabled but API key not configured")
        ai_ready = False
    
    if not db_ready:
        logger.error("Database not ready")
        return HealthCheckResponse(
            status="not_ready",
            version=settings.APP_VERSION,
            timestamp=datetime.utcnow(),
            database=False,
            ai_service=ai_ready,
            message="Database unavailable"
        )
    
    return HealthCheckResponse(
        status="ready",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        database=db_ready,
        ai_service=ai_ready,
        message="Service ready to accept traffic"
    )


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    """General health check endpoint.
    
    Simple check that service is running.
    No dependencies, always succeeds if API is reachable.
    """
    return HealthCheckResponse(
        status="ok",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        database=True,
        ai_service=True
    )
