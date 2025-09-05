"""
Authentication schemas for the AuthService
Includes request/response models for all authentication operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    org_id: int = Field(..., description="Organization ID for the user")
    service_id: int = Field(..., description="Service ID for the user")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Schema for user registration response"""
    user_id: int = Field(..., description="User ID")
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


class UserProfileResponse(BaseModel):
    """Schema for user profile response with roles and organization info"""
    user: Dict[str, Any] = Field(..., description="User information")
    roles: List[Dict[str, Any]] = Field(..., description="User roles")
    organization: Optional[Dict[str, Any]] = Field(None, description="Organization information")
    subscriptions: List[Dict[str, Any]] = Field(..., description="Organization subscriptions")


class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="Overall service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment name")
    database_status: str = Field(..., description="Database connection status")
    uptime: float = Field(..., description="Service uptime in seconds")