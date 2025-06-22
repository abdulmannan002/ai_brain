"""
User data models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Fallback for EmailStr if not available
try:
    from pydantic import EmailStr
except ImportError:
    EmailStr = str  # Fallback to regular string


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr = Field(..., description="User email address")
    subscription: str = Field(default="free", description="User subscription tier")


class UserCreate(UserBase):
    """Model for creating a new user"""
    auth0_id: str = Field(..., description="Auth0 user ID")


class UserUpdate(BaseModel):
    """Model for updating a user"""
    email: Optional[EmailStr] = None
    subscription: Optional[str] = None


class User(UserBase):
    """Complete user model"""
    id: int
    auth0_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """User response model for API"""
    id: int
    email: str
    subscription: str
    
    class Config:
        from_attributes = True


class UserStats(BaseModel):
    """User statistics model"""
    total_ideas: int
    ideas_this_month: int
    projects_count: int
    themes_count: int
    emotions_count: int 