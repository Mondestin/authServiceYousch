"""
User model for the AuthService
Includes comprehensive user information and authentication fields for multi-tenant system
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey, Enum, BigInteger
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    User model representing authenticated users in the system
    
    Note: Users can login even if their email is not verified (is_verified=False).
    Email verification is still tracked but not required for authentication.
    
    Fields:
        id: Unique identifier for the user
        email: User's email address (unique)
        username: User's username (unique)
        hashed_password: Securely hashed password
        full_name: User's full name
        is_active: Whether the user account is active
        is_verified: Whether the user's email is verified (not required for login)
        is_superuser: Whether the user has superuser privileges
        created_at: When the user account was created
        updated_at: When the user account was last updated
        last_login: When the user last logged in
        failed_login_attempts: Number of consecutive failed login attempts
        locked_until: When the account is locked until (if locked)
        email_verification_token: Token for email verification
        password_reset_token: Token for password reset
        password_reset_expires: When the password reset token expires
        profile_picture_url: URL to user's profile picture
        phone_number: User's phone number
        date_of_birth: User's date of birth
        address: User's address
        preferences: JSON string for user preferences
        metadata: Additional user metadata
    """
    
    __tablename__ = "users"
    
    # Primary key - using BIGINT for MySQL compatibility
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True, comment="User ID")
    
    # Multi-tenant fields
    school_id = Column(BIGINT, ForeignKey("schools.id", ondelete="CASCADE"), nullable=False, index=True)
    campus_id = Column(BIGINT, ForeignKey("campuses.id", ondelete="CASCADE"), nullable=True, index=True)
    role_id = Column(BIGINT, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Authentication fields
    email = Column(String(255), nullable=False, index=True)  # Not unique globally, unique per school
    username = Column(String(50), nullable=True, index=True)  # Optional, unique per school
    phone = Column(String(20), nullable=True, index=True)  # Optional, unique per school
    hashed_password = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(Enum('male', 'female', 'other', name='gender_enum'), nullable=True)
    profile_picture = Column(String(255), nullable=True)
    
    # Status fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)  # Email verification status (not required for login)
    
    # Security fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    # Verification and reset tokens
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    school = relationship("School", back_populates="users")
    campus = relationship("Campus", back_populates="users")
    role = relationship("Role", back_populates="users")
    login_history = relationship("LoginHistory", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")  # Only one active session allowed per user
    
    def __repr__(self) -> str:
        """String representation of the user"""
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive fields)"""
        return {
            "id": self.id,
            "school_id": self.school_id,
            "campus_id": self.campus_id,
            "role_id": self.role_id,
            "email": self.email,
            "username": self.username,
            "phone": self.phone,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender": self.gender,
            "profile_picture": self.profile_picture,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
    
    @property
    def is_locked(self) -> bool:
        """Check if the user account is currently locked"""
        if self.locked_until is None:
            return False
        return datetime.now() < self.locked_until
    
    @property
    def can_login(self) -> bool:
        """Check if the user can currently log in"""
        # Allow login even if email is not verified
        # Only check if account is active and not locked
        return self.is_active and not self.is_locked
    
    @property
    def full_name(self) -> str:
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return "Unknown"
    
    def increment_failed_login_attempts(self) -> None:
        """Increment failed login attempts counter"""
        self.failed_login_attempts += 1
    
    def reset_failed_login_attempts(self) -> None:
        """Reset failed login attempts counter"""
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def lock_account(self, lock_duration_minutes: int = 30) -> None:
        """Lock the user account for a specified duration"""
        from datetime import timedelta
        self.locked_until = datetime.now() + timedelta(minutes=lock_duration_minutes)
    
    def update_last_login(self) -> None:
        """Update the last login timestamp"""
        self.last_login = datetime.now()
        self.reset_failed_login_attempts()


class UserSession(Base):
    """
    User session model for tracking active sessions
    
    Note: Only one active session is allowed per user at a time.
    When a new session is created, all existing active sessions are deactivated.
    
    Fields:
        id: Unique identifier for the session
        user_id: Reference to the user
        session_token: Unique session token
        refresh_token: Refresh token for the session
        ip_address: IP address where session was created
        user_agent: User agent string
        is_active: Whether the session is active
        expires_at: When the session expires
        created_at: When the session was created
        last_used: When the session was last used
    """
    
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(BIGINT, primary_key=True, autoincrement=True, index=True)
    
    # Foreign key to user
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session tokens
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Session metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_used = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self) -> str:
        """String representation of the session"""
        return f"<UserSession(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
    
    def is_expired(self) -> bool:
        """Check if the session has expired"""
        return datetime.now() > self.expires_at
    
    def update_last_used(self) -> None:
        """Update the last used timestamp"""
        self.last_used = datetime.now()
    
    def deactivate(self) -> None:
        """Deactivate the session"""
        self.is_active = False 