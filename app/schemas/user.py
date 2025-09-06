"""
User schemas for AuthGhost API
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    is_active: Optional[bool] = Field(None, description="Whether user is active")
    roles: Optional[List[int]] = Field(None, description="List of role IDs")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int = Field(..., description="User ID")
    org_id: int = Field(..., description="Organization ID")
    email: str = Field(..., description="User's email address")
    first_name: Optional[str] = Field(None, description="User's first name")
    last_name: Optional[str] = Field(None, description="User's last name")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True