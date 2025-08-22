"""
Main API router for the AuthService
Includes all endpoint modules and sets up the API structure
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, schools, campuses, roles, users

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(campuses.router, prefix="/campuses", tags=["campuses"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(users.router, prefix="/users", tags=["users"]) 