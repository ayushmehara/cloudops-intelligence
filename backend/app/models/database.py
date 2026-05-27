"""
Database connection and session management.

Handles SQLAlchemy setup and database connections.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create base class for all models
Base = declarative_base()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,
    poolclass=NullPool,  # No connection pooling for K8s
    connect_args={"connect_timeout": 10}
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    """Get database session.
    
    FastAPI dependency for injecting database sessions.
    Yields session and ensures cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables.
    
    Creates all tables defined in models.
    Safe to call multiple times.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def check_db_connection():
    """Check database connectivity.
    
    Used for health checks.
    Returns True if connected, False otherwise.
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
