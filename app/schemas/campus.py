"""
Campus schemas for the AuthService
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator


class CampusBase(BaseModel):
    """Base campus schema with common fields"""
    name: str = Field(..., description="Campus name", min_length=1, max_length=255)
    address_street: Optional[str] = Field(None, description="Street address", max_length=255)
    address_city: Optional[str] = Field(None, description="City", max_length=100)
    address_postal: Optional[str] = Field(None, description="Postal code", max_length=20)
    address_country: Optional[str] = Field(None, description="Country", max_length=100)
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone", max_length=50)
    
    @validator('contact_email')
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v is not None and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class CampusCreate(CampusBase):
    """Schema for creating a new campus"""
    school_id: int = Field(..., description="School ID for the campus")


class CampusUpdate(BaseModel):
    """Schema for updating a campus"""
    name: Optional[str] = Field(None, description="Campus name", min_length=1, max_length=255)
    address_street: Optional[str] = Field(None, description="Street address", max_length=255)
    address_city: Optional[str] = Field(None, description="City", max_length=100)
    address_postal: Optional[str] = Field(None, description="Postal code", max_length=20)
    address_country: Optional[str] = Field(None, description="Country", max_length=100)
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, description="Contact phone", max_length=50)
    
    @validator('contact_email')
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v is not None and '@' not in v:
            raise ValueError('Invalid email format')
        return v


class CampusResponse(CampusBase):
    """Schema for campus responses"""
    id: int = Field(..., description="Campus unique identifier")
    school_id: int = Field(..., description="School ID for the campus")
    created_at: datetime = Field(..., description="When the campus was created")
    updated_at: datetime = Field(..., description="When the campus was last updated")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CampusListResponse(BaseModel):
    """Schema for campus list responses"""
    campuses: list[CampusResponse] = Field(..., description="List of campuses")
    total: int = Field(..., description="Total number of campuses")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True 