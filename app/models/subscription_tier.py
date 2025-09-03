"""
SubscriptionTier model for the AuthService
Represents service-specific subscription tiers
"""

from datetime import datetime
from sqlalchemy import Column, String, BigInteger, ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubscriptionTier(Base):
    """
    SubscriptionTier model representing service-specific subscription tiers
    
    Fields:
        id: Unique identifier for the subscription tier
        service_id: Reference to the service
        tier_name: Name of the subscription tier
        features: JSON object containing tier features
        created_at: When the subscription tier was created
    """
    
    __tablename__ = "subscription_tiers"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys
    service_id = Column(BIGINT, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tier information
    tier_name = Column(String(50), nullable=False)
    features = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    service = relationship("Service", back_populates="subscription_tiers")
    subscriptions = relationship("OrganizationSubscription", back_populates="tier")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('service_id', 'tier_name', name='unique_service_tier'),
    )
    
    def __repr__(self) -> str:
        """String representation of the subscription tier"""
        return f"<SubscriptionTier(id={self.id}, tier_name='{self.tier_name}', service_id={self.service_id})>"
    
    def to_dict(self) -> dict:
        """Convert subscription tier to dictionary"""
        return {
            "id": self.id,
            "service_id": self.service_id,
            "tier_name": self.tier_name,
            "features": self.features,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }