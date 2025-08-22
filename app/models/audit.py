"""
Audit models for tracking user activities and security events
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, BigInteger, ForeignKey, Enum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class LoginHistory(Base):
    """
    Login history model for tracking user authentication attempts
    
    Fields:
        id: Unique identifier for the login record
        user_id: Reference to the user
        ip_address: IP address of the login attempt
        device_info: Device information (user agent, etc.)
        login_time: When the login attempt occurred
        status: Whether the login was successful or failed
    """
    
    __tablename__ = "login_history"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Foreign key to user
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Login attempt information
    ip_address = Column(String(100), nullable=True)  # IPv6 compatible
    device_info = Column(Text, nullable=True)
    login_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(Enum('success', 'failed', name='login_status'), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="login_history")
    
    def __repr__(self) -> str:
        """String representation of the login history"""
        return f"<LoginHistory(id={self.id}, user_id={self.user_id}, status='{self.status}', time='{self.login_time}')>"
    
    def to_dict(self) -> dict:
        """Convert login history to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "device_info": self.device_info,
            "login_time": self.login_time.isoformat() if self.login_time else None,
            "status": self.status
        }
    
    @property
    def is_successful(self) -> bool:
        """Check if the login was successful"""
        return self.status == 'success'
    
    @property
    def is_failed(self) -> bool:
        """Check if the login failed"""
        return self.status == 'failed' 