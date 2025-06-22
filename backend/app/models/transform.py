"""
Transformation data models
"""
from typing import Literal
from pydantic import BaseModel, Field


class TransformRequest(BaseModel):
    """Model for transformation request"""
    idea_id: int = Field(..., description="ID of the idea to transform")
    output_type: Literal["content", "ip", "tasks"] = Field(..., description="Type of transformation")
    user_id: str = Field(..., description="User ID")


class TransformResponse(BaseModel):
    """Model for transformation response"""
    transformed_content: str = Field(..., description="Generated transformation content")
    idea_id: int = Field(..., description="ID of the transformed idea")
    output_type: str = Field(..., description="Type of transformation performed")


class TransformPrompt(BaseModel):
    """Model for transformation prompts"""
    content: str = Field(..., description="Original idea content")
    output_type: str = Field(..., description="Type of transformation")
    prompt: str = Field(..., description="Generated prompt for AI") 