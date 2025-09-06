"""
Organization schemas for AuthGhost API
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(..., min_length=1, max_length=255, description="Organization name")


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization"""
    pass


class OrganizationUpdate(BaseModel):
    """Schema for updating an organization"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Organization name")


class OrganizationResponse(OrganizationBase):
    """Schema for organization response"""
    id: int = Field(..., description="Organization ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True