"""
Subscription tier schemas for the AuthService
"""

from typing import Dict, Any
from pydantic import BaseModel, Field


class SubscriptionTierBase(BaseModel):
    """Base subscription tier schema"""
    service_id: int = Field(..., description="Service ID")
    tier_name: str = Field(..., min_length=1, max_length=50, description="Tier name")
    features: Dict[str, Any] = Field(..., description="Tier features as JSON")


class SubscriptionTierCreate(SubscriptionTierBase):
    """Schema for creating a subscription tier"""
    pass


class SubscriptionTierUpdate(BaseModel):
    """Schema for updating a subscription tier"""
    tier_name: str = Field(None, min_length=1, max_length=50, description="Tier name")
    features: Dict[str, Any] = Field(None, description="Tier features as JSON")


class SubscriptionTierResponse(SubscriptionTierBase):
    """Schema for subscription tier response"""
    id: int = Field(..., description="Subscription tier ID")
    created_at: str = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True