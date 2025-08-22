"""
Authentication schemas for the AuthService
Includes request/response models for all authentication operations
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr = Field(..., description="User's email address")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="User's username")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    gender: Optional[str] = Field(None, description="User's gender (male/female/other)")


class UserCreate(UserBase):
    """Schema for user registration"""
    school_id: int = Field(..., description="School ID for the user")
    campus_id: Optional[int] = Field(None, description="Campus ID for the user (optional)")
    role_id: int = Field(..., description="Role ID for the user")
    password: str = Field(..., min_length=8, description="User's password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username contains only alphanumeric characters and underscores"""
        if v and not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    first_name: Optional[str] = Field(None, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    date_of_birth: Optional[datetime] = Field(None, description="User's date of birth")
    gender: Optional[str] = Field(None, description="User's gender (male/female/other)")
    profile_picture: Optional[str] = Field(None, max_length=255, description="Profile picture path")


class UserResponse(UserBase):
    """Schema for user responses (excluding sensitive data)"""
    id: int = Field(..., description="User's unique identifier")
    school_id: int = Field(..., description="School ID for the user")
    campus_id: Optional[int] = Field(None, description="Campus ID for the user")
    role_id: int = Field(..., description="Role ID for the user")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user's email is verified")
    created_at: datetime = Field(..., description="When the user account was created")
    updated_at: datetime = Field(..., description="When the user account was last updated")
    last_login: Optional[datetime] = Field(None, description="When the user last logged in")
    profile_picture: Optional[str] = Field(None, description="Profile picture path")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    remember_me: Optional[bool] = Field(False, description="Whether to remember the user")


class TokenResponse(BaseModel):
    """Schema for token responses"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    refresh_expires_in: int = Field(..., description="Refresh token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token requests"""
    refresh_token: str = Field(..., description="JWT refresh token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset requests"""
    email: EmailStr = Field(..., description="User's email address")


class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class EmailVerification(BaseModel):
    """Schema for email verification"""
    token: str = Field(..., description="Email verification token")


class ChangePassword(BaseModel):
    """Schema for password change"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        """Validate that passwords match"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserSessionResponse(BaseModel):
    """Schema for user session responses"""
    id: int = Field(..., description="Session unique identifier")
    user_id: int = Field(..., description="User's unique identifier")
    ip_address: Optional[str] = Field(None, description="IP address where session was created")
    user_agent: Optional[str] = Field(None, description="User agent string")
    is_active: bool = Field(..., description="Whether the session is active")
    expires_at: datetime = Field(..., description="When the session expires")
    created_at: datetime = Field(..., description="When the session was created")
    last_used: datetime = Field(..., description="When the session was last used")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LoginAttempt(BaseModel):
    """Schema for login attempt tracking"""
    email: EmailStr = Field(..., description="User's email address")
    ip_address: str = Field(..., description="IP address of the login attempt")
    user_agent: str = Field(..., description="User agent string")
    success: bool = Field(..., description="Whether the login attempt was successful")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the attempt occurred")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SecurityEvent(BaseModel):
    """Schema for security events"""
    event_type: str = Field(..., description="Type of security event")
    severity: str = Field(..., description="Severity level of the event")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    ip_address: str = Field(..., description="IP address where the event occurred")
    user_agent: str = Field(..., description="User agent string")
    details: dict = Field(default_factory=dict, description="Additional event details")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the event occurred")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HealthCheck(BaseModel):
    """Schema for health check responses"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment name")
    database_status: str = Field(..., description="Database connection status")
    uptime: float = Field(..., description="Service uptime in seconds")
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 