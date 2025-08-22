"""
Authentication endpoints for the AuthService
Includes registration, login, logout, and token management
"""

import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_user,
    get_current_active_user,
    get_db,
    get_client_ip,
    get_user_agent,
    check_rate_limit,
    validate_password_strength,
    sanitize_input_data
)
from app.core.config import get_settings
from app.core.logging import get_logger, log_auth_event, log_security_event
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_secure_token
)
from app.models.user import User, UserSession
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordReset,
    EmailVerification,
    ChangePassword
)

# Get settings and logger
settings = get_settings()
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user account
    
    Args:
        user_data: User registration data
        request: FastAPI request object
        db: Database session
        
    Returns:
        UserResponse: Created user information
        
    Raises:
        HTTPException: If registration fails
    """
    # Check rate limiting
    check_rate_limit(request, "/auth/register")
    
    # Sanitize input data
    user_data.email = sanitize_input_data(user_data.email)
    user_data.username = sanitize_input_data(user_data.username)
    if user_data.first_name:
        user_data.first_name = sanitize_input_data(user_data.first_name)
    if user_data.last_name:
        user_data.last_name = sanitize_input_data(user_data.last_name)
    
    # Validate password strength
    validate_password_strength(user_data.password)
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    try:
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        
        # Generate email verification token
        verification_token = generate_secure_token()
        
        new_user = User(
            school_id=user_data.school_id,
            campus_id=user_data.campus_id,
            role_id=user_data.role_id,
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            date_of_birth=user_data.date_of_birth,
            gender=user_data.gender,
            email_verification_token=verification_token
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Log successful registration
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        log_auth_event(
            event_type="user_registered",
            user_id=str(new_user.id),
            details={
                "email": new_user.email,
                "username": new_user.username,
                "ip_address": client_ip,
                "user_agent": user_agent
            }
        )
        
        logger.info("User registered successfully", 
                   user_id=str(new_user.id),
                   email=new_user.email)
        
        # Send email verification email
        try:
            from app.core.email import send_email_verification
            await send_email_verification(
                to_email=new_user.email,
                username=new_user.username or new_user.email,
                verification_token=verification_token,
                user_id=str(new_user.id)
            )
        except Exception as e:
            logger.warning("Failed to send verification email", 
                          user_id=str(new_user.id),
                          error=str(e))
            # Don't fail registration if email sending fails
        
        # Send welcome email with credentials
        try:
            from app.core.email import send_welcome_email
            await send_welcome_email(
                to_email=new_user.email,
                username=new_user.username or new_user.email,
                password=user_data.password,  # Plain text password for welcome email
                user_id=str(new_user.id)
            )
        except Exception as e:
            logger.warning("Failed to send welcome email", 
                          user_id=str(new_user.id),
                          error=str(e))
            # Don't fail registration if email sending fails
        
        return UserResponse.model_validate(new_user)
        
    except Exception as e:
        db.rollback()
        logger.error("User registration failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Authenticate user and return access tokens
    
    Args:
        user_credentials: User login credentials
        request: FastAPI request object
        db: Database session
        
    Returns:
        TokenResponse: Access and refresh tokens with user information
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check rate limiting
    check_rate_limit(request, "/auth/login")
    
    # Sanitize input data
    user_credentials.email = sanitize_input_data(user_credentials.email)
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user:
            # Log failed login attempt
            client_ip = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            log_security_event(
                event_type="failed_login_attempt",
                severity="warning",
                details={
                    "email": user_credentials.email,
                    "ip_address": client_ip,
                    "user_agent": user_agent,
                    "reason": "user_not_found"
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user can login (email verification not required)
        if not user.can_login:
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account is deactivated"
                )
            elif user.is_locked:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account is temporarily locked"
                )
        
        # Verify password
        if not verify_password(user_credentials.password, user.hashed_password):
            # Increment failed login attempts
            user.increment_failed_login_attempts()
            
            # Lock account if too many failed attempts
            if user.failed_login_attempts >= 5:
                user.lock_account(30)  # Lock for 30 minutes
                logger.warning("User account locked due to failed login attempts", 
                             user_id=str(user.id))
            
            db.commit()
            
            # Log failed login attempt
            client_ip = get_client_ip(request)
            user_agent = get_user_agent(request)
            
            log_security_event(
                event_type="failed_login_attempt",
                severity="warning",
                details={
                    "user_id": str(user.id),
                    "email": user.email,
                    "ip_address": client_ip,
                    "user_agent": user_agent,
                    "failed_attempts": user.failed_login_attempts,
                    "reason": "invalid_password"
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Reset failed login attempts and update last login
        user.reset_failed_login_attempts()
        user.update_last_login()
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
            user_id=str(user.id)
        )
        
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=refresh_token_expires,
            user_id=str(user.id)
        )
        
        # Deactivate any existing active sessions for this user (ensure only one active token at a time)
        existing_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True
        ).all()
        
        for existing_session in existing_sessions:
            existing_session.deactivate()
            logger.info("Deactivated existing session", 
                       user_id=str(user.id),
                       session_id=str(existing_session.id))
        
        # Create new user session
        session = UserSession(
            user_id=user.id,
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            expires_at=datetime.now() + refresh_token_expires
        )
        
        db.add(session)
        db.commit()
        
        # Log successful login
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        log_auth_event(
            event_type="user_login",
            user_id=str(user.id),
            details={
                "ip_address": client_ip,
                "user_agent": user_agent,
                "remember_me": user_credentials.remember_me
            }
        )
        
        logger.info("User logged in successfully", 
                   user_id=str(user.id),
                   email=user.email)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using refresh token
    
    Args:
        refresh_data: Refresh token data
        request: FastAPI request object
        db: Database session
        
    Returns:
        TokenResponse: New access and refresh tokens
        
    Raises:
        HTTPException: If token refresh fails
    """
    # Check rate limiting
    check_rate_limit(request, "/auth/refresh")
    
    try:
        # Verify refresh token
        payload = verify_token(refresh_data.refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Find user session
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_data.refresh_token,
            UserSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        if session.is_expired():
            session.deactivate()
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.can_login:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        
        new_access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires,
            user_id=str(user.id)
        )
        
        new_refresh_token = create_refresh_token(
            data={"sub": str(user.id)},
            expires_delta=refresh_token_expires,
            user_id=str(user.id)
        )
        
        # Deactivate any other active sessions for this user (ensure only one active token at a time)
        other_active_sessions = db.query(UserSession).filter(
            UserSession.user_id == user.id,
            UserSession.is_active == True,
            UserSession.id != session.id
        ).all()
        
        for other_session in other_active_sessions:
            other_session.deactivate()
            logger.info("Deactivated other active session during refresh", 
                       user_id=str(user.id),
                       session_id=str(other_session.id))
        
        # Update current session
        old_refresh_token = session.refresh_token
        session.session_token = new_access_token
        session.refresh_token = new_refresh_token
        session.expires_at = datetime.now() + refresh_token_expires
        session.update_last_used()
        
        db.commit()
        
        # Log token refresh
        log_auth_event(
            event_type="token_refreshed",
            user_id=str(user.id),
            details={
                "ip_address": get_client_ip(request),
                "user_agent": get_user_agent(request)
            }
        )
        
        logger.info("Token refreshed successfully", user_id=str(user.id))
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
            user=UserResponse.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Logout user and invalidate session
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Logout confirmation message
    """
    try:
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Deactivate session
            session = db.query(UserSession).filter(
                UserSession.session_token == token,
                UserSession.user_id == current_user.id,
                UserSession.is_active == True
            ).first()
            
            if session:
                session.deactivate()
                db.commit()
        
        # Log logout
        log_auth_event(
            event_type="user_logout",
            user_id=str(current_user.id),
            details={
                "ip_address": get_client_ip(request),
                "user_agent": get_user_agent(request)
            }
        )
        
        logger.info("User logged out successfully", user_id=str(current_user.id))
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerification,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    Verify user email address
    
    Args:
        verification_data: Email verification data
        request: FastAPI request object
        db: Database session
        
    Returns:
        dict: Verification confirmation message
        
    Raises:
        HTTPException: If verification fails
    """
    # Check rate limiting
    check_rate_limit(request, "/auth/verify-email")
    
    try:
        # Find user by verification token
        user = db.query(User).filter(
            User.email_verification_token == verification_data.token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Verify email
        user.is_verified = True
        user.email_verification_token = None
        db.commit()
        
        # Log email verification
        log_auth_event(
            event_type="email_verified",
            user_id=str(user.id),
            details={
                "ip_address": get_client_ip(request),
                "user_agent": get_user_agent(request)
            }
        )
        
        logger.info("Email verified successfully", 
                   user_id=str(user.id),
                   email=user.email)
        
        return {"message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Email verification failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.post("/request-password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    Request password reset
    
    Args:
        reset_request: Password reset request data
        request: FastAPI request object
        db: Database session
        
    Returns:
        dict: Password reset request confirmation message
    """
    # Check rate limiting
    check_rate_limit(request, "/auth/request-password-reset")
    
    # Sanitize input data
    reset_request.email = sanitize_input_data(reset_request.email)
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == reset_request.email).first()
        
        if user:
            # Generate password reset token
            reset_token = generate_secure_token()
            reset_expires = datetime.now() + timedelta(hours=24)
            
            user.password_reset_token = reset_token
            user.password_reset_expires = reset_expires
            db.commit()
            
            # Send password reset email
            try:
                from app.core.email import send_password_reset
                await send_password_reset(
                    to_email=user.email,
                    username=user.username or user.email,
                    reset_token=reset_token,
                    user_id=str(user.id)
                )
            except Exception as e:
                logger.warning("Failed to send password reset email", 
                              user_id=str(user.id),
                              error=str(e))
                # Don't fail password reset request if email sending fails
            
            # Log password reset request
            log_auth_event(
                event_type="password_reset_requested",
                user_id=str(user.id),
                details={
                    "ip_address": get_client_ip(request),
                    "user_agent": get_user_agent(request)
                }
            )
            
            logger.info("Password reset requested", 
                       user_id=str(user.id),
                       email=user.email)
        
        # Always return success to prevent email enumeration
        return {"message": "If the email exists, a password reset link has been sent"}
        
    except Exception as e:
        logger.error("Password reset request failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    request: Request,
    db: Session = Depends(get_db)
) -> dict:
    """
    Reset password using reset token
    
    Args:
        reset_data: Password reset data
        request: FastAPI request object
        db: Database session
        
    Returns:
        dict: Password reset confirmation message
        
    Raises:
        HTTPException: If password reset fails
    """
    # Check rate limiting
    check_rate_limit(request, "/auth/reset-password")
    
    # Validate password strength
    validate_password_strength(reset_data.new_password)
    
    try:
        # Find user by reset token
        user = db.query(User).filter(
            User.password_reset_token == reset_data.token
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Check if token is expired
        if user.password_reset_expires and datetime.now() > user.password_reset_expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token expired"
            )
        
        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        
        # Log password reset
        log_auth_event(
            event_type="password_reset_completed",
            user_id=str(user.id),
            details={
                "ip_address": get_client_ip(request),
                "user_agent": get_user_agent(request)
            }
        )
        
        logger.info("Password reset completed", 
                   user_id=str(user.id),
                   email=user.email)
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password reset failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Change user password
    
    Args:
        password_data: Password change data
        request: FastAPI request object
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        dict: Password change confirmation message
        
    Raises:
        HTTPException: If password change fails
    """
    # Validate password strength
    validate_password_strength(password_data.new_password)
    
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        current_user.hashed_password = get_password_hash(password_data.new_password)
        db.commit()
        
        # Log password change
        log_auth_event(
            event_type="password_changed",
            user_id=str(current_user.id),
            details={
                "ip_address": get_client_ip(request),
                "user_agent": get_user_agent(request)
            }
        )
        
        logger.info("Password changed successfully", user_id=str(current_user.id))
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Password change failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user information
    """
    return UserResponse.model_validate(current_user) 