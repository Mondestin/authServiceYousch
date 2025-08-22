"""
Security utilities for the AuthService
Includes JWT token handling, password hashing, and security functions
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.logging import get_logger, log_security_event

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error("Password verification error", error=str(e))
        log_security_event(
            event_type="password_verification_error",
            severity="error",
            details={"error": str(e)}
        )
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: The plain text password to hash
        
    Returns:
        str: The hashed password
        
    Raises:
        SecurityError: If password hashing fails
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error("Password hashing error", error=str(e))
        log_security_event(
            event_type="password_hashing_error",
            severity="error",
            details={"error": str(e)}
        )
        raise SecurityError("Failed to hash password") from e


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Create a JWT access token
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        user_id: Optional user ID for logging
        
    Returns:
        str: The encoded JWT token
        
    Raises:
        SecurityError: If token creation fails
    """
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        
        logger.info("Access token created", user_id=user_id, expires_at=expire.isoformat())
        return encoded_jwt
        
    except Exception as e:
        logger.error("Access token creation error", error=str(e), user_id=user_id)
        log_security_event(
            event_type="token_creation_error",
            severity="error",
            details={"error": str(e), "user_id": user_id}
        )
        raise SecurityError("Failed to create access token") from e


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        user_id: Optional user ID for logging
        
    Returns:
        str: The encoded JWT refresh token
        
    Raises:
        SecurityError: If token creation fails
    """
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(
                days=settings.refresh_token_expire_days
            )
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        
        logger.info("Refresh token created", user_id=user_id, expires_at=expire.isoformat())
        return encoded_jwt
        
    except Exception as e:
        logger.error("Refresh token creation error", error=str(e), user_id=user_id)
        log_security_event(
            event_type="token_creation_error",
            severity="error",
            details={"error": str(e), "user_id": user_id}
        )
        raise SecurityError("Failed to create refresh token") from e


def verify_token(token: str, user_id: Optional[str] = None) -> Optional[dict]:
    """
    Verify and decode a JWT token
    
    Args:
        token: The JWT token to verify
        user_id: Optional user ID for logging
        
    Returns:
        Optional[dict]: The decoded token data or None if invalid
        
    Raises:
        SecurityError: If token verification fails
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Check if token is expired
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if datetime.now().timestamp() > exp_timestamp:
                logger.warning("Token expired", user_id=user_id, exp_timestamp=exp_timestamp)
                log_security_event(
                    event_type="token_expired",
                    severity="warning",
                    details={"user_id": user_id, "exp_timestamp": exp_timestamp}
                )
                return None
        
        logger.info("Token verified successfully", user_id=user_id)
        return payload
        
    except JWTError as e:
        logger.warning("Token verification failed", error=str(e), user_id=user_id)
        log_security_event(
            event_type="token_verification_failed",
            severity="warning",
            details={"error": str(e), "user_id": user_id}
        )
        return None
    except Exception as e:
        logger.error("Unexpected token verification error", error=str(e), user_id=user_id)
        log_security_event(
            event_type="token_verification_error",
            severity="error",
            details={"error": str(e), "user_id": user_id}
        )
        raise SecurityError("Failed to verify token") from e


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token
    
    Args:
        length: The length of the token in bytes
        
    Returns:
        str: The generated secure token
    """
    return secrets.token_urlsafe(length)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password strength requirements
    
    Args:
        password: The password to validate
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def sanitize_input(input_string: str) -> str:
    """
    Basic input sanitization to prevent injection attacks
    
    Args:
        input_string: The input string to sanitize
        
    Returns:
        str: The sanitized string
    """
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", ";", "|", "`", "$", "(", ")", "{", "}"]
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized.strip()


def rate_limit_key(client_ip: str, endpoint: str) -> str:
    """
    Generate a rate limiting key for a client and endpoint
    
    Args:
        client_ip: The client's IP address
        endpoint: The API endpoint being accessed
        
    Returns:
        str: The rate limiting key
    """
    return f"rate_limit:{client_ip}:{endpoint}"


def is_suspicious_activity(
    client_ip: str,
    endpoint: str,
    user_agent: str,
    request_count: int
) -> bool:
    """
    Detect suspicious activity based on request patterns
    
    Args:
        client_ip: The client's IP address
        endpoint: The API endpoint being accessed
        user_agent: The client's user agent string
        request_count: Number of requests in the current time window
        
    Returns:
        bool: True if suspicious activity is detected
    """
    # Check for excessive requests
    if request_count > settings.rate_limit_per_minute * 2:
        logger.warning("Excessive requests detected", 
                      client_ip=client_ip, 
                      endpoint=endpoint, 
                      request_count=request_count)
        return True
    
    # Check for suspicious user agent
    suspicious_agents = ["bot", "crawler", "scraper", "spider", "curl", "wget"]
    if any(agent in user_agent.lower() for agent in suspicious_agents):
        logger.info("Suspicious user agent detected", 
                   client_ip=client_ip, 
                   user_agent=user_agent)
        return True
    
    return False 