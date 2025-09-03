"""
Service model for the AuthService
Represents services in the microservices architecture
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, DateTime, BigInteger
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Service(Base):
    """
    Service model representing a microservice in the system
    
    Fields:
        id: Unique identifier for the service
        name: Service name (unique)
        description: Service description
        status: Service status (active/inactive)
        created_at: When the service was created
    """
    
    __tablename__ = "services"
    
    # Primary key - using BIGINT for MySQL compatibility
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True, comment="Service ID")
    
    # Service information
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    status = Column(Enum('active', 'inactive', name='service_status'), default='active', nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    roles = relationship("Role", back_populates="service", cascade="all, delete-orphan")
    subscription_tiers = relationship("SubscriptionTier", back_populates="service", cascade="all, delete-orphan")
    subscriptions = relationship("OrganizationSubscription", back_populates="service", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the service"""
        return f"<Service(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def to_dict(self) -> dict:
        """Convert service to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }