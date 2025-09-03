"""
Token management endpoints for the AuthService
Includes JWT token revocation and listing
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.logging import get_logger
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.schemas.token import TokenRevokeRequest, RevokedTokenResponse

# Get logger
logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/revoke", status_code=status.HTTP_200_OK)
def revoke_token(
    token_data: TokenRevokeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoke a JWT token
    Only accessible by super_admin
    """
    # TODO: Add super_admin role check
    # For now, allowing any authenticated user
    
    # Check if token is already revoked
    existing_revoked_token = db.query(RevokedToken).filter(
        RevokedToken.token_id == token_data.token_id
    ).first()
    if existing_revoked_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is already revoked"
        )
    
    # Create revoked token record
    revoked_token = RevokedToken(
        token_id=token_data.token_id,
        user_id=current_user.id  # Assuming the current user is revoking the token
    )
    
    db.add(revoked_token)
    db.commit()
    
    logger.info(f"Token revoked: {token_data.token_id} by user {current_user.id}")
    return {"message": "Token revoked successfully"}


@router.get("/", response_model=List[RevokedTokenResponse])
def get_tokens(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of active/revoked tokens
    Optional user_id filter
    Accessible by super_admin and org_admin
    """
    # TODO: Add super_admin and org_admin role checks
    # For now, allowing any authenticated user
    
    query = db.query(RevokedToken)
    if user_id:
        query = query.filter(RevokedToken.user_id == user_id)
    
    tokens = query.all()
    return tokens