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


class ServiceDetails(BaseModel):
    """Service details for user profile response"""
    id: int = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    description: Optional[str] = Field(None, description="Service description")
    status: str = Field(..., description="Service status")
    
    class Config:
        from_attributes = True


class SubscriptionTierDetails(BaseModel):
    """Subscription tier details for user profile response"""
    id: int = Field(..., description="Subscription tier ID")
    service_id: int = Field(..., description="Service ID")
    tier_name: str = Field(..., description="Tier name")
    features: dict = Field(..., description="Tier features")
    
    class Config:
        from_attributes = True


class RoleDetails(BaseModel):
    """Role details for user profile response"""
    id: int = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    service_id: int = Field(..., description="Service ID")
    permissions: dict = Field(..., description="Role permissions")
    service: ServiceDetails = Field(..., description="Service details")
    
    class Config:
        from_attributes = True


class OrganizationDetails(BaseModel):
    """Organization details for user profile response"""
    id: int = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    created_at: Optional[str] = Field(None, description="Organization creation date")
    updated_at: Optional[str] = Field(None, description="Organization last update date")
    
    class Config:
        from_attributes = True


class SubscriptionDetails(BaseModel):
    """Subscription details for user profile response"""
    id: int = Field(..., description="Subscription ID")
    service_id: int = Field(..., description="Service ID")
    tier_id: int = Field(..., description="Tier ID")
    start_date: str = Field(..., description="Subscription start date")
    end_date: str = Field(..., description="Subscription end date")
    is_active: bool = Field(..., description="Whether subscription is active")
    service: ServiceDetails = Field(..., description="Service details")
    tier: SubscriptionTierDetails = Field(..., description="Tier details")
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Schema for user profile response with full details"""
    user: Dict[str, Any] = Field(..., description="User information including roles, organization, and subscriptions")


class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Current timestamp")
    uptime: float = Field(..., description="Service uptime in seconds")
    version: str = Field(..., description="Service version")
    database: Dict[str, Any] = Field(..., description="Database status")
    environment: str = Field(..., description="Environment name")