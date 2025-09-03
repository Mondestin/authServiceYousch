"""
Service schemas for the AuthService
"""

from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ServiceBase(BaseModel):
    """Base service schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Service name")
    description: Optional[str] = Field(None, max_length=255, description="Service description")
    status: ServiceStatus = Field(ServiceStatus.ACTIVE, description="Service status")


class ServiceCreate(ServiceBase):
    """Schema for creating a service"""
    pass


class ServiceUpdate(BaseModel):
    """Schema for updating a service"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Service name")
    description: Optional[str] = Field(None, max_length=255, description="Service description")
    status: Optional[ServiceStatus] = Field(None, description="Service status")


class ServiceResponse(ServiceBase):
    """Schema for service response"""
    id: int = Field(..., description="Service ID")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True