"""
Organization model for the AuthService
Represents organizations in the multi-tenant system
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, BigInteger
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Organization(Base):
    """
    Organization model representing a tenant in the multi-tenant system
    
    Fields:
        id: Unique identifier for the organization
        name: Organization name (unique)
        created_at: When the organization was created
        updated_at: When the organization was last updated
    """
    
    __tablename__ = "organizations"
    
    # Primary key - using BIGINT for MySQL compatibility
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True, comment="Organization ID")
    
    # Organization information
    name = Column(String(255), nullable=False, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    subscriptions = relationship("OrganizationSubscription", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the organization"""
        return f"<Organization(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convert organization to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }