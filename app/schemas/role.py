"""
Role schemas for the AuthService
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class RoleCreate(BaseModel):
    """Schema for creating a role"""
    name: str = Field(..., min_length=1, max_length=50, description="Role name")
    service_id: int = Field(..., description="Service ID")
    permissions: Dict[str, Any] = Field(..., description="Role permissions as JSON")


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: str = Field(None, min_length=1, max_length=50, description="Role name")
    permissions: Dict[str, Any] = Field(None, description="Role permissions as JSON")


class RoleResponse(BaseModel):
    """Schema for role response"""
    id: int = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    service_id: int = Field(..., description="Service ID")
    permissions: Dict[str, Any] = Field(..., description="Role permissions as JSON")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True