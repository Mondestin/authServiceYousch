"""
Role model for the AuthService
Represents service-specific roles with JSON permissions
"""

from datetime import datetime
from sqlalchemy import Column, String, BigInteger, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    """
    Role model for service-specific role-based access control
    
    Fields:
        id: Unique identifier for the role
        name: Role name
        service_id: Reference to the service
        permissions: JSON object containing permissions
        created_at: When the role was created
    """
    
    __tablename__ = "roles"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Role information
    name = Column(String(50), nullable=False)
    service_id = Column(BIGINT, ForeignKey("services.id", ondelete="CASCADE"), nullable=False, index=True)
    permissions = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    service = relationship("Service", back_populates="roles")
    user_roles = relationship("UserRole", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the role"""
        return f"<Role(id={self.id}, name='{self.name}', service_id={self.service_id})>"
    
    def to_dict(self) -> dict:
        """Convert role to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "service_id": self.service_id,
            "permissions": self.permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }