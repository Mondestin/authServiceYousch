"""
Role schemas for AuthGhost API
"""

from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field, field_validator
import json


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
    created_at: datetime = Field(..., description="Creation timestamp")
    
    @field_validator('permissions', mode='before')
    @classmethod
    def parse_permissions(cls, v):
        """Parse permissions field - handle both JSON strings and dictionaries"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return v
        return v
    
    class Config:
        from_attributes = True