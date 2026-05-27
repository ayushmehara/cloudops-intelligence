"""
Incident management API routes.

Handle incident tracking, AI analysis, and resolution.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from app.models.database import get_db
from app.models.schemas import Incident
from app.models.pydantic_schemas import (
    IncidentCreate, IncidentResponse, IncidentUpdate
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/incidents", tags=["incidents"])


@router.post("/", response_model=IncidentResponse)
def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    """Create a new incident/alert.
    
    Args:
        incident: Incident creation payload
        db: Database session
    
    Returns:
        Created incident object
    
    Example:
        POST /api/incidents
        {
            "title": "High error rate in backend",
            "severity": "critical",
            "service": "backend",
            "description": "Error rate jumped to 15%"
        }
    """
    try:
        db_incident = Incident(
            title=incident.title,
            description=incident.description,
            severity=incident.severity,
            service=incident.service,
            status="open",
            metrics=incident.metrics,
            logs=incident.logs,
            related_deployment_id=incident.related_deployment_id
        )
        
        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)
        
        logger.info(f"Incident created: {db_incident.id}, severity: {incident.severity}")
        return db_incident
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """Get specific incident by ID."""
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return incident


@router.get("/", response_model=list[IncidentResponse])
def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    severity: str = Query(None),
    status: str = Query(None),
    service: str = Query(None),
    db: Session = Depends(get_db)
):
    """List incidents with filters.
    
    Example:
        GET /api/incidents?severity=critical&status=open
    """
    query = db.query(Incident)
    
    # Apply filters
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    if service:
        query = query.filter(Incident.service == service)
    
    # Order by created_at descending
    query = query.order_by(desc(Incident.created_at))
    
    # Pagination
    incidents = query.offset(skip).limit(limit).all()
    
    return incidents


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident(
    incident_id: str,
    update: IncidentUpdate,
    db: Session = Depends(get_db)
):
    """Update incident status and analysis.
    
    Example:
        PATCH /api/incidents/{id}
        {
            "status": "resolved",
            "resolved_at": "2024-01-15T10:30:00",
            "ai_analysis": "Root cause was database connection pool exhaustion"
        }
    """
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Update fields
    if update.status:
        incident.status = update.status
    if update.resolved_at:
        incident.resolved_at = update.resolved_at
    if update.ai_analysis:
        incident.ai_analysis = update.ai_analysis
    
    db.commit()
    db.refresh(incident)
    
    logger.info(f"Incident updated: {incident_id}, status: {incident.status}")
    return incident


@router.get("/{incident_id}/stats")
def get_incident_stats(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """Get incident statistics and metrics."""
    incident = db.query(Incident).filter(
        Incident.id == incident_id
    ).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Calculate stats
    duration = None
    if incident.resolved_at and incident.created_at:
        duration = (incident.resolved_at - incident.created_at).total_seconds()
    
    return {
        "incident_id": incident_id,
        "title": incident.title,
        "severity": incident.severity,
        "status": incident.status,
        "duration_seconds": duration,
        "created_at": incident.created_at,
        "resolved_at": incident.resolved_at,
        "metric_count": len(incident.metrics) if incident.metrics else 0,
        "log_lines": len(incident.logs) if incident.logs else 0
    }
