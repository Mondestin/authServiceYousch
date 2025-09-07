"""
Organization subscription schemas for AuthGhost API
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class ServiceDetails(BaseModel):
    """Service details for organization subscription response"""
    id: int = Field(..., description="Service ID")
    name: str = Field(..., description="Service name")
    description: Optional[str] = Field(None, description="Service description")
    status: str = Field(..., description="Service status")
    
    class Config:
        from_attributes = True


class SubscriptionTierDetails(BaseModel):
    """Subscription tier details for organization subscription response"""
    id: int = Field(..., description="Subscription tier ID")
    service_id: int = Field(..., description="Service ID")
    tier_name: str = Field(..., description="Tier name")
    features: dict = Field(..., description="Tier features")
    
    class Config:
        from_attributes = True


class OrganizationSubscriptionBase(BaseModel):
    """Base organization subscription schema"""
    org_id: int = Field(..., description="Organization ID")
    service_id: int = Field(..., description="Service ID")
    tier_id: int = Field(..., description="Subscription tier ID")
    start_date: date = Field(..., description="Subscription start date")
    end_date: date = Field(..., description="Subscription end date")
    is_active: Optional[bool] = Field(True, description="Whether subscription is active")


class OrganizationSubscriptionCreate(OrganizationSubscriptionBase):
    """Schema for creating an organization subscription"""
    pass


class OrganizationSubscriptionUpdate(BaseModel):
    """Schema for updating an organization subscription"""
    tier_id: Optional[int] = Field(None, description="Subscription tier ID")
    start_date: Optional[date] = Field(None, description="Subscription start date")
    end_date: Optional[date] = Field(None, description="Subscription end date")
    is_active: Optional[bool] = Field(None, description="Whether subscription is active")


class OrganizationSubscriptionResponse(OrganizationSubscriptionBase):
    """Schema for organization subscription response with full details"""
    id: int = Field(..., description="Organization subscription ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    service: ServiceDetails = Field(..., description="Service details")
    tier: SubscriptionTierDetails = Field(..., description="Subscription tier details")
    
    class Config:
        from_attributes = True