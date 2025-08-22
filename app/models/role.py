"""
Role and Permission models for the RBAC system
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, BigInteger, ForeignKey, Boolean
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Role(Base):
    """
    Role model for role-based access control
    
    Fields:
        id: Unique identifier for the role
        school_id: Reference to the school (null for global roles)
        campus_id: Reference to the campus (null for school-level or global roles)
        name: Role name
        description: Role description
        is_default: Whether this is a default role
        created_at: When the role was created
        updated_at: When the role was last updated
    """
    
    __tablename__ = "roles"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Foreign keys (nullable for global roles)
    school_id = Column(BIGINT, ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True)
    campus_id = Column(BIGINT, ForeignKey("campuses.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Role information
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    school = relationship("School", back_populates="roles")
    campus = relationship("Campus", back_populates="roles")
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the role"""
        return f"<Role(id={self.id}, name='{self.name}', school_id={self.school_id}, campus_id={self.campus_id})>"
    
    def to_dict(self) -> dict:
        """Convert role to dictionary"""
        return {
            "id": self.id,
            "school_id": self.school_id,
            "campus_id": self.campus_id,
            "name": self.name,
            "description": self.description,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def is_global(self) -> bool:
        """Check if this is a global role (no school or campus)"""
        return self.school_id is None and self.campus_id is None
    
    @property
    def is_school_level(self) -> bool:
        """Check if this is a school-level role"""
        return self.school_id is not None and self.campus_id is None
    
    @property
    def is_campus_level(self) -> bool:
        """Check if this is a campus-level role"""
        return self.campus_id is not None


class Permission(Base):
    """
    Permission model for granular access control
    
    Fields:
        id: Unique identifier for the permission
        name: Permission name (unique)
        description: Permission description
        created_at: When the permission was created
    """
    
    __tablename__ = "permissions"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Permission information
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    roles = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the permission"""
        return f"<Permission(id={self.id}, name='{self.name}')>"
    
    def to_dict(self) -> dict:
        """Convert permission to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RolePermission(Base):
    """
    Junction table for many-to-many relationship between roles and permissions
    
    Fields:
        role_id: Reference to the role
        permission_id: Reference to the permission
    """
    
    __tablename__ = "role_permissions"
    
    # Composite primary key
    role_id = Column(BIGINT, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id = Column(BIGINT, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
    
    def __repr__(self) -> str:
        """String representation of the role permission"""
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>" 