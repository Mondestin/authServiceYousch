"""
Organization subscription schemas for authGhost API
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


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
    """Schema for organization subscription response"""
    id: int = Field(..., description="Organization subscription ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True