"""
SQLAlchemy ORM models for database tables.

Defines all data structures stored in PostgreSQL.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.database import Base
import uuid


class User(Base):
    """User account model."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deployments = relationship("Deployment", back_populates="created_by_user")
    incidents = relationship("Incident", back_populates="created_by_user")


class Deployment(Base):
    """Deployment tracking model."""
    __tablename__ = "deployments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    application = Column(String, index=True, nullable=False)
    environment = Column(String, index=True, nullable=False)  # prod/staging/dev
    version = Column(String, nullable=False)
    image = Column(String, nullable=False)  # Docker image
    status = Column(String, default="pending")  # pending/success/failed/rolling_back
    duration_seconds = Column(Integer)  # How long deployment took
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
    git_commit = Column(String)  # Git commit SHA
    git_branch = Column(String)
    rollback_from = Column(String, ForeignKey("deployments.id"))  # If rollback
    metadata = Column(JSON)  # Extra deployment info
    
    # Relationships
    created_by_user = relationship("User", back_populates="deployments", foreign_keys=[created_by])
    incidents = relationship("Incident", back_populates="related_deployment")


class Incident(Base):
    """Incident/alert tracking model."""
    __tablename__ = "incidents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String, index=True)  # critical/high/medium/low
    status = Column(String, default="open")  # open/investigating/resolved/ignored
    service = Column(String, index=True, nullable=False)
    related_deployment_id = Column(String, ForeignKey("deployments.id"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    created_by = Column(String, ForeignKey("users.id"))
    ai_analysis = Column(Text)  # AI-generated RCA
    ai_suggested_action = Column(Text)
    metrics = Column(JSON)  # Related metrics
    logs = Column(JSON)  # Related log lines
    
    # Relationships
    created_by_user = relationship("User", back_populates="incidents", foreign_keys=[created_by])
    related_deployment = relationship("Deployment", back_populates="incidents")


class Metric(Base):
    """Metrics data model (simplified)."""
    __tablename__ = "metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    service = Column(String, index=True, nullable=False)
    value = Column(Float, nullable=False)
    labels = Column(JSON)  # Prometheus-style labels
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class Configuration(Base):
    """Application configuration storage."""
    __tablename__ = "configurations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String)
    is_secret = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
