"""
Main API router for the AuthService
Includes all endpoint modules and sets up the API structure
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, health, users, roles, services, 
    subscription_tiers, organization_subscriptions, tokens
)

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(subscription_tiers.router, prefix="/subscription-tiers", tags=["subscription-tiers"])
api_router.include_router(organization_subscriptions.router, prefix="/organization-subscriptions", tags=["organization-subscriptions"])
api_router.include_router(tokens.router, prefix="/tokens", tags=["tokens"]) 