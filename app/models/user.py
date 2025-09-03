"""
User model for the AuthService
Includes user information and authentication fields for multi-tenant system
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, BigInteger, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    User model representing authenticated users in the system
    
    Fields:
        id: Unique identifier for the user
        org_id: Reference to the organization
        email: User's email address (unique)
        password_hash: Securely hashed password
        is_active: Whether the user account is active
        created_at: When the user account was created
        updated_at: When the user account was last updated
        last_login: When the user last logged in
    """
    
    __tablename__ = "users"
    
    # Primary key - using BIGINT for MySQL compatibility
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True, comment="User ID")
    
    # Multi-tenant fields
    org_id = Column(BIGINT, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Authentication fields
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    user_roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    revoked_tokens = relationship("RevokedToken", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the user"""
        return f"<User(id={self.id}, email='{self.email}')>"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive fields)"""
        return {
            "id": self.id,
            "org_id": self.org_id,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.now() 