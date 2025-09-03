"""
UserRole model for the AuthService
Represents the many-to-many relationship between users and roles
"""

from datetime import datetime
from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(Base):
    """
    UserRole model representing the many-to-many relationship between users and roles
    
    Fields:
        id: Unique identifier for the user role
        user_id: Reference to the user
        role_id: Reference to the role
        created_at: When the user role was created
    """
    
    __tablename__ = "user_roles"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(BIGINT, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='unique_user_role'),
    )
    
    def __repr__(self) -> str:
        """String representation of the user role"""
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"
    
    def to_dict(self) -> dict:
        """Convert user role to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }