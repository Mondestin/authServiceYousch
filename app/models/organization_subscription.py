"""
OrganizationSubscription model for the AuthService
Represents organization subscriptions to services with specific tiers
"""

from datetime import datetime, date
from sqlalchemy import Column, BigInteger, ForeignKey, Date, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrganizationSubscription(Base):
    """
    OrganizationSubscription model representing organization subscriptions to services
    
    Fields:
        id: Unique identifier for the subscription
        org_id: Reference to the organization
        service_id: Reference to the service
        tier_id: Reference to the subscription tier
        start_date: Subscription start date
        end_date: Subscription end date
        is_active: Whether the subscription is active
        created_at: When the subscription was created
    """
    
    __tablename__ = "organization_subscriptions"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys
    org_id = Column(BIGINT, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    service_id = Column(BIGINT, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    tier_id = Column(BIGINT, ForeignKey("subscription_tiers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Subscription information
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="subscriptions")
    service = relationship("Service", back_populates="subscriptions")
    tier = relationship("SubscriptionTier", back_populates="subscriptions")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('org_id', 'service_id', name='unique_org_service'),
    )
    
    def __repr__(self) -> str:
        """String representation of the organization subscription"""
        return f"<OrganizationSubscription(id={self.id}, org_id={self.org_id}, service_id={self.service_id})>"
    
    def to_dict(self) -> dict:
        """Convert organization subscription to dictionary"""
        return {
            "id": self.id,
            "org_id": self.org_id,
            "service_id": self.service_id,
            "tier_id": self.tier_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }