"""
Models package for the AuthService
"""

from .user import User, UserSession
from .school import School, Campus
from .role import Role, Permission, RolePermission
from .audit import LoginHistory

__all__ = [
    "User", "UserSession",
    "School", "Campus", 
    "Role", "Permission", "RolePermission",
    "LoginHistory"
] 