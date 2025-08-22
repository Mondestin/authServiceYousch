"""
School and Campus models for the multi-tenant authentication service
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, BigInteger, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class School(Base):
    """
    School model representing a tenant in the multi-tenant system
    
    Fields:
        id: Unique identifier for the school
        name: School name
        code: Unique school code
        domain: School domain
        created_at: When the school was created
        updated_at: When the school was last updated
    """
    
    __tablename__ = "schools"
    
    # Primary key - using BIGINT for MySQL compatibility
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True, comment="School ID")
    
    # School information
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    campuses = relationship("Campus", back_populates="school", cascade="all, delete-orphan")
    users = relationship("User", back_populates="school", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="school", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the school"""
        return f"<School(id={self.id}, name='{self.name}', code='{self.code}')>"
    
    def to_dict(self) -> dict:
        """Convert school to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "domain": self.domain,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Campus(Base):
    """
    Campus model representing a physical location of a school
    
    Fields:
        id: Unique identifier for the campus
        school_id: Reference to the school
        name: Campus name
        address_street: Street address
        address_city: City
        address_postal: Postal code
        address_country: Country
        contact_email: Contact email
        contact_phone: Contact phone
        created_at: When the campus was created
        updated_at: When the campus was last updated
    """
    
    __tablename__ = "campuses"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Foreign key to school
    school_id = Column(BIGINT, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Campus information
    name = Column(String(255), nullable=False)
    address_street = Column(String(255), nullable=True)
    address_city = Column(String(100), nullable=True)
    address_postal = Column(String(20), nullable=True)
    address_country = Column(String(100), nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    school = relationship("School", back_populates="campuses")
    users = relationship("User", back_populates="campus", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="campus", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of the campus"""
        return f"<Campus(id={self.id}, name='{self.name}', school_id={self.school_id})>"
    
    def to_dict(self) -> dict:
        """Convert campus to dictionary"""
        return {
            "id": self.id,
            "school_id": self.school_id,
            "name": self.name,
            "address_street": self.address_street,
            "address_city": self.address_city,
            "address_postal": self.address_postal,
            "address_country": self.address_country,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        } 