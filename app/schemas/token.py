"""
Token schemas for AuthGhost API
"""

from datetime import datetime
from pydantic import BaseModel, Field


class TokenRevokeRequest(BaseModel):
    """Schema for token revocation request"""
    token_id: str = Field(..., description="JWT token ID to revoke")


class RevokedTokenResponse(BaseModel):
    """Schema for revoked token response"""
    id: int = Field(..., description="Revoked token record ID")
    token_id: str = Field(..., description="JWT token ID")
    user_id: int = Field(..., description="User ID who owned the token")
    revoked_at: datetime = Field(..., description="Revocation timestamp")
    
    class Config:
        from_attributes = True