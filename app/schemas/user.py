"""
User schemas for the AuthService
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: str = Field(..., description="User's email address")
    username: Optional[str] = Field(None, description="User's username", max_length=50)
    phone: Optional[str] = Field(None, description="User's phone number", max_length=20)
    first_name: Optional[str] = Field(None, description="User's first name", max_length=100)
    last_name: Optional[str] = Field(None, description="User's last name", max_length=100)
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    gender: Optional[str] = Field(None, description="User's gender")
    profile_picture: Optional[str] = Field(None, description="URL to user's profile picture", max_length=255)
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format"""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('gender')
    def validate_gender(cls, v):
        """Validate gender value"""
        if v is not None and v not in ['male', 'female', 'other']:
            raise ValueError('Gender must be one of: male, female, other')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user"""
    school_id: int = Field(..., description="School ID for the user")
    campus_id: Optional[int] = Field(None, description="Campus ID for the user (optional)")
    role_id: int = Field(..., description="Role ID for the user")
    hashed_password: str = Field(..., description="Hashed password")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = Field(None, description="User's username", max_length=50)
    phone: Optional[str] = Field(None, description="User's phone number", max_length=20)
    first_name: Optional[str] = Field(None, description="User's first name", max_length=100)
    last_name: Optional[str] = Field(None, description="User's last name", max_length=100)
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    gender: Optional[str] = Field(None, description="User's gender")
    profile_picture: Optional[str] = Field(None, description="URL to user's profile picture", max_length=255)
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")
    is_verified: Optional[bool] = Field(None, description="Whether the user's email is verified")
    
    @validator('gender')
    def validate_gender(cls, v):
        """Validate gender value if provided"""
        if v is not None and v not in ['male', 'female', 'other']:
            raise ValueError('Gender must be one of: male, female, other')
        return v


class UserResponse(UserBase):
    """Schema for user responses"""
    id: int = Field(..., description="User unique identifier")
    school_id: int = Field(..., description="School ID for the user")
    campus_id: Optional[int] = Field(None, description="Campus ID for the user")
    role_id: int = Field(..., description="Role ID for the user")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user's email is verified")
    created_at: datetime = Field(..., description="When the user account was created")
    updated_at: datetime = Field(..., description="When the user account was last updated")
    last_login: Optional[datetime] = Field(None, description="When the user last logged in")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserListResponse(BaseModel):
    """Schema for user list responses"""
    users: list[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum number of records returned")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True


class UserPasswordUpdate(BaseModel):
    """Schema for updating user password"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password", min_length=8)
    confirm_password: str = Field(..., description="Confirm new password")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Ensure passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v 