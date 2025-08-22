"""
API dependencies for the AuthService
Includes authentication, rate limiting, and database session management
"""

import time
from typing import Generator, Optional
from uuid import uuid4

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_database_session, SessionLocal
from app.core.logging import get_logger, log_request_info, log_response_info
from app.core.security import verify_token, is_suspicious_activity
from app.models.user import User

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Security scheme
security = HTTPBearer()


def get_request_id() -> str:
    """Generate a unique request ID for tracking"""
    return str(uuid4())


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers first (for proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("User-Agent", "unknown")


def log_request_middleware(request: Request, request_id: str):
    """Log incoming request information"""
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    log_request_info(
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=client_ip,
        user_agent=user_agent
    )


def log_response_middleware(request_id: str, status_code: int, response_time: float):
    """Log response information"""
    log_response_info(
        request_id=request_id,
        status_code=status_code,
        response_time=response_time
    )


def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        logger.error("Database session error", error=str(e))
        session.rollback()
        raise
    finally:
        session.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        token = credentials.credentials
        payload = verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user account"
            )
        
        # Email verification is no longer required for authentication
        # Users can login even if their email is not verified
        
        logger.info("User authenticated successfully", user_id=str(user.id))
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (additional check for active status)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current verified user (additional check for email verification)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current verified user
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified"
        )
    return current_user


def get_current_school_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current school admin (additional check for school admin privileges)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current school admin
        
    Raises:
        HTTPException: If user is not a school admin
    """
    # Check if user has school admin role
    if not current_user.role.is_school_level or current_user.role.name not in ["School Admin", "Principal"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="School admin privileges required"
        )
    return current_user


def get_current_campus_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current campus admin (additional check for campus admin privileges)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current campus admin
        
    Raises:
        HTTPException: If user is not a campus admin
    """
    # Check if user has campus admin role
    if not current_user.role.is_campus_level or current_user.role.name not in ["Campus Admin", "Manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Campus admin privileges required"
        )
    return current_user


def check_permission(permission_name: str):
    """
    Dependency to check if user has a specific permission
    
    Args:
        permission_name: Name of the permission to check
        
    Returns:
        Function that checks the permission
    """
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        # Check if user has the required permission
        user_permissions = [rp.permission.name for rp in current_user.role.permissions]
        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required"
            )
        return current_user
    
    return permission_checker


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current superuser (additional check for superuser privileges)
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    # Check if user has a global super admin role
    if not current_user.role.is_global or current_user.role.name != "Super Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    return current_user


def check_rate_limit(
    request: Request,
    endpoint: str,
    max_requests: int = None,
    window_seconds: int = 60
) -> None:
    """
    Check rate limiting for the current request
    
    Args:
        request: FastAPI request object
        endpoint: API endpoint being accessed
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    if max_requests is None:
        max_requests = settings.rate_limit_per_minute
    
    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Check for suspicious activity
    if is_suspicious_activity(client_ip, endpoint, user_agent, 0):
        logger.warning("Suspicious activity detected", 
                      client_ip=client_ip, 
                      endpoint=endpoint, 
                      user_agent=user_agent)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Suspicious activity detected"
        )
    
    # TODO: Implement actual rate limiting logic with Redis or database
    # For now, this is a placeholder that always allows requests
    logger.debug("Rate limit check passed", 
                client_ip=client_ip, 
                endpoint=endpoint)


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    
    Args:
        credentials: Optional HTTP authorization credentials
        db: Database session
        
    Returns:
        Optional[User]: Current authenticated user or None
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def validate_password_strength(password: str) -> None:
    """
    Validate password strength requirements
    
    Args:
        password: Password to validate
        
    Raises:
        HTTPException: If password doesn't meet requirements
    """
    from app.core.security import validate_password_strength as validate_pwd
    
    is_valid, errors = validate_pwd(password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {'; '.join(errors)}"
        )


def sanitize_input_data(data: str) -> str:
    """
    Sanitize input data to prevent injection attacks
    
    Args:
        data: Input data to sanitize
        
    Returns:
        str: Sanitized data
    """
    from app.core.security import sanitize_input
    return sanitize_input(data) 