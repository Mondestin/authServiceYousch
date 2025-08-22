"""
Schemas package for the AuthService
"""

from .auth import *
from .school import *
from .campus import *
from .role import *
from .user import *

__all__ = [
    # Auth schemas
    "UserLogin", "UserRegister", "TokenResponse", "RefreshTokenRequest",
    "ChangePassword", "UserSessionResponse", "LoginAttempt",
    
    # School schemas
    "SchoolCreate", "SchoolUpdate", "SchoolResponse", "SchoolListResponse",
    
    # Campus schemas
    "CampusCreate", "CampusUpdate", "CampusResponse", "CampusListResponse",
    
    # Role schemas
    "RoleCreate", "RoleUpdate", "RoleResponse", "RoleListResponse",
    "PermissionResponse", "PermissionListResponse",
    
    # User schemas
    "UserCreate", "UserUpdate", "UserResponse", "UserListResponse", "UserPasswordUpdate"
] 