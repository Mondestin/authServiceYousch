"""
School schemas for the AuthService
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class SchoolBase(BaseModel):
    """Base school schema with common fields"""
    name: str = Field(..., description="School name", min_length=1, max_length=255)
    code: str = Field(..., description="Unique school code", min_length=1, max_length=50)
    domain: str = Field(..., description="School domain", min_length=1, max_length=255)
    
    @validator('code')
    def validate_code(cls, v):
        """Validate school code format"""
        if not v.isalnum() and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('School code must contain only alphanumeric characters, hyphens, and underscores')
        return v.upper()
    
    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain format"""
        if not v.startswith('http://') and not v.startswith('https://'):
            v = 'https://' + v
        return v


class SchoolCreate(SchoolBase):
    """Schema for creating a new school"""
    pass


class SchoolUpdate(BaseModel):
    """Schema for updating a school"""
    name: Optional[str] = Field(None, description="School name", min_length=1, max_length=255)
    code: Optional[str] = Field(None, description="Unique school code", min_length=1, max_length=50)
    domain: Optional[str] = Field(None, description="School domain", min_length=1, max_length=255)
    
    @validator('code')
    def validate_code(cls, v):
        """Validate school code format if provided"""
        if v is not None:
            if not v.isalnum() and not v.replace('-', '').replace('_', '').isalnum():
                raise ValueError('School code must contain only alphanumeric characters, hyphens, and underscores')
            return v.upper()
        return v
    
    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain format if provided"""
        if v is not None:
            if not v.startswith('http://') and not v.startswith('https://'):
                v = 'https://' + v
        return v


class SchoolResponse(SchoolBase):
    """Schema for school responses"""
    id: int = Field(..., description="School unique identifier")
    created_at: datetime = Field(..., description="When the school was created")
    updated_at: datetime = Field(..., description="When the school was last updated")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SchoolListResponse(BaseModel):
    """Schema for school list responses"""
    schools: list[SchoolResponse] = Field(..., description="List of schools")
    total: int = Field(..., description="Total number of schools")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True 