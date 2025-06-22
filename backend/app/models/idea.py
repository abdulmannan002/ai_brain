"""
Idea data models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class IdeaBase(BaseModel):
    """Base idea model"""
    content: str = Field(..., min_length=1, max_length=10000, description="Idea content")
    source: str = Field(default="manual", description="Source of the idea")


class IdeaCreate(IdeaBase):
    """Model for creating a new idea"""
    pass


class IdeaUpdate(BaseModel):
    """Model for updating an idea"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    project: Optional[str] = Field(None, max_length=100)
    theme: Optional[str] = Field(None, max_length=100)
    emotion: Optional[str] = Field(None, max_length=50)
    transformed_output: Optional[str] = Field(None)


class Idea(IdeaBase):
    """Complete idea model"""
    id: int
    user_id: str
    timestamp: datetime
    project: Optional[str] = None
    theme: Optional[str] = None
    emotion: Optional[str] = None
    transformed_output: Optional[str] = None
    
    class Config:
        from_attributes = True


class IdeaResponse(BaseModel):
    """Idea response model for API"""
    id: int
    content: str
    source: str
    timestamp: datetime
    project: Optional[str] = None
    theme: Optional[str] = None
    emotion: Optional[str] = None
    transformed_output: Optional[str] = None
    
    class Config:
        from_attributes = True


class IdeaAnalysis(BaseModel):
    """Idea analysis model"""
    id: int
    content: str
    project: Optional[str] = None
    theme: Optional[str] = None
    emotion: Optional[str] = None


class IdeaSearchParams(BaseModel):
    """Idea search parameters"""
    q: Optional[str] = None
    project: Optional[str] = None
    theme: Optional[str] = None
    emotion: Optional[str] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=100) 