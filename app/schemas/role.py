"""
Role and Permission schemas for the AuthService
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class RoleBase(BaseModel):
    """Base role schema with common fields"""
    name: str = Field(..., description="Role name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Role description")
    is_default: bool = Field(False, description="Whether this is a default role")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate role name format"""
        if not v.replace(' ', '').replace('-', '').replace('_', '').isalnum():
            raise ValueError('Role name must contain only alphanumeric characters, spaces, hyphens, and underscores')
        return v


class RoleCreate(RoleBase):
    """Schema for creating a new role"""
    school_id: Optional[int] = Field(None, description="School ID (null for global roles)")
    campus_id: Optional[int] = Field(None, description="Campus ID (null for school-level or global roles)")


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    name: Optional[str] = Field(None, description="Role name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Role description")
    is_default: Optional[bool] = Field(None, description="Whether this is a default role")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate role name format if provided"""
        if v is not None:
            if not v.replace(' ', '').replace('-', '').replace('_', '').isalnum():
                raise ValueError('Role name must contain only alphanumeric characters, spaces, hyphens, and underscores')
        return v


class RoleResponse(RoleBase):
    """Schema for role responses"""
    id: int = Field(..., description="Role unique identifier")
    school_id: Optional[int] = Field(None, description="School ID (null for global roles)")
    campus_id: Optional[int] = Field(None, description="Campus ID (null for school-level or global roles)")
    created_at: datetime = Field(..., description="When the role was created")
    updated_at: datetime = Field(..., description="When the role was last updated")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PermissionResponse(BaseModel):
    """Schema for permission responses"""
    id: int = Field(..., description="Permission unique identifier")
    name: str = Field(..., description="Permission name")
    description: Optional[str] = Field(None, description="Permission description")
    created_at: datetime = Field(..., description="When the permission was created")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RoleListResponse(BaseModel):
    """Schema for role list responses"""
    roles: list[RoleResponse] = Field(..., description="List of roles")
    total: int = Field(..., description="Total number of roles")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True


class PermissionListResponse(BaseModel):
    """Schema for permission list responses"""
    permissions: list[PermissionResponse] = Field(..., description="List of permissions")
    total: int = Field(..., description="Total number of permissions")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True 