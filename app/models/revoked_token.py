"""
RevokedToken model for the AuthService
Represents revoked JWT tokens for security purposes
"""

from datetime import datetime
from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class RevokedToken(Base):
    """
    RevokedToken model for tracking revoked JWT tokens
    
    Fields:
        id: Unique identifier for the revoked token record
        token_id: JWT token ID (jti claim)
        user_id: Reference to the user who owned the token
        revoked_at: When the token was revoked
    """
    
    __tablename__ = "revoked_tokens"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Token information
    token_id = Column(String(255), nullable=False, index=True)
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    revoked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="revoked_tokens")
    
    def __repr__(self) -> str:
        """String representation of the revoked token"""
        return f"<RevokedToken(id={self.id}, token_id='{self.token_id}', user_id={self.user_id})>"
    
    def to_dict(self) -> dict:
        """Convert revoked token to dictionary"""
        return {
            "id": self.id,
            "token_id": self.token_id,
            "user_id": self.user_id,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None
        }