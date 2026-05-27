"""
Pydantic schemas for request/response validation.

Separate from SQLAlchemy models for cleaner separation.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ USER SCHEMAS ============
class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Create user request."""
    password: str = Field(..., min_length=8)


