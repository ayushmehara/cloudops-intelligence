"""
Deployment management API routes.

CRUD operations for deployments.
Tracks deployment history, status, and rollbacks.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime
from app.models.database import get_db
from app.models.schemas import Deployment
from app.models.pydantic_schemas import (
    DeploymentCreate, DeploymentResponse, DeploymentUpdate
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/deployments", tags=["deployments"])


@router.post("/", response_model=DeploymentResponse)
def create_deployment(
    deployment: DeploymentCreate,
    db: Session = Depends(get_db)
):
    """Create a new deployment.
    
    Args:
        deployment: Deployment creation payload
        db: Database session (injected)
    
    Returns:
        Created deployment object
    
    Example:
        POST /api/deployments
        {
            "name": "backend-v2.1.0",
            "application": "backend",
            "environment": "production",
            "version": "2.1.0",
            "image": "myregistry/backend:2.1.0",
            "git_commit": "abc123def456",
            "git_branch": "main"
        }
    """
    try:
        # Create deployment object
        db_deployment = Deployment(
            name=deployment.name,
            application=deployment.application,
            environment=deployment.environment,
            version=deployment.version,
            image=deployment.image,
            git_commit=deployment.git_commit,
            git_branch=deployment.git_branch,
            metadata=deployment.metadata,
            status="pending"
        )
        
        # Save to database
        db.add(db_deployment)
        db.commit()
        db.refresh(db_deployment)
        
        logger.info(f"Deployment created: {db_deployment.id}")
        return db_deployment
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create deployment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{deployment_id}", response_model=DeploymentResponse)
def get_deployment(
    deployment_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific deployment by ID.
    
    Args:
        deployment_id: Deployment UUID
        db: Database session (injected)
    
    Returns:
        Deployment object
    
    Raises:
        HTTPException 404: Deployment not found
    """
    deployment = db.query(Deployment).filter(
        Deployment.id == deployment_id
    ).first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return deployment


@router.get("/", response_model=list[DeploymentResponse])
def list_deployments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    application: str = Query(None),
    environment: str = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """List deployments with filters.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Number of records to return (max 100)
        application: Filter by application name
        environment: Filter by environment (prod/staging/dev)
        status: Filter by status
        db: Database session (injected)
    
    Returns:
        List of deployments matching filters
    
    Example:
        GET /api/deployments?application=backend&environment=production&limit=50
    """
    query = db.query(Deployment)
    
    # Apply filters
    if application:
        query = query.filter(Deployment.application == application)
    if environment:
        query = query.filter(Deployment.environment == environment)
    if status:
        query = query.filter(Deployment.status == status)
    
    # Order by created_at descending (newest first)
    query = query.order_by(desc(Deployment.created_at))
    
    # Pagination
    deployments = query.offset(skip).limit(limit).all()
    
    return deployments


@router.patch("/{deployment_id}", response_model=DeploymentResponse)
def update_deployment(
    deployment_id: str,
    update: DeploymentUpdate,
    db: Session = Depends(get_db)
):
    """Update deployment status.
    
    Args:
        deployment_id: Deployment UUID
        update: Update payload (status, duration, etc)
        db: Database session (injected)
    
    Returns:
        Updated deployment object
    
    Example:
        PATCH /api/deployments/{id}
        {
            "status": "success",
            "duration_seconds": 300,
            "completed_at": "2024-01-15T10:30:00"
        }
    """
    deployment = db.query(Deployment).filter(
        Deployment.id == deployment_id
    ).first()
    
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Update fields
    if update.status:
        deployment.status = update.status
    if update.duration_seconds is not None:
        deployment.duration_seconds = update.duration_seconds
    if update.completed_at:
        deployment.completed_at = update.completed_at
    
    deployment.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(deployment)
    
    logger.info(f"Deployment updated: {deployment_id}, status: {deployment.status}")
    return deployment


@router.post("/{deployment_id}/rollback", response_model=DeploymentResponse)
def rollback_deployment(
    deployment_id: str,
    db: Session = Depends(get_db)
):
    """Rollback to previous deployment.
    
    Creates a new deployment marking it as rollback.
    Does not delete previous deployment.
    
    Args:
        deployment_id: Deployment UUID to rollback from
        db: Database session (injected)
    
    Returns:
        New rollback deployment object
    
    Example:
        POST /api/deployments/{id}/rollback
    """
    # Find current deployment
    current = db.query(Deployment).filter(
        Deployment.id == deployment_id
    ).first()
    
    if not current:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Find previous successful deployment
    previous = db.query(Deployment).filter(
        and_(
            Deployment.application == current.application,
            Deployment.environment == current.environment,
            Deployment.status == "success",
            Deployment.created_at < current.created_at
        )
    ).order_by(desc(Deployment.created_at)).first()
    
    if not previous:
        raise HTTPException(
            status_code=400,
            detail="No previous successful deployment found"
        )
    
    # Create rollback deployment
    rollback = Deployment(
        name=f"rollback-{current.version}-to-{previous.version}",
        application=current.application,
        environment=current.environment,
        version=previous.version,
        image=previous.image,
        status="pending",
        rollback_from=deployment_id,
        git_commit=previous.git_commit,
        git_branch=previous.git_branch
    )
    
    db.add(rollback)
    db.commit()
    db.refresh(rollback)
    
    logger.warning(f"Rollback initiated: {rollback.id}, from {deployment_id}")
    return rollback


@router.get("/{deployment_id}/history", response_model=list[DeploymentResponse])
def get_deployment_history(
    deployment_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get deployment history for an application.
    
    Args:
        deployment_id: Deployment UUID to get history for
        limit: Number of records to return
        db: Database session (injected)
    
    Returns:
        List of deployments in reverse chronological order
    """
    # Get the reference deployment
    ref = db.query(Deployment).filter(
        Deployment.id == deployment_id
    ).first()
    
    if not ref:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    # Get history for same app/environment
    history = db.query(Deployment).filter(
        and_(
            Deployment.application == ref.application,
            Deployment.environment == ref.environment
        )
    ).order_by(desc(Deployment.created_at)).limit(limit).all()
    
    return history
