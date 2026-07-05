"""
Authentication Dependencies
FastAPI dependencies for protected routes
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from backend.shared.database.connection import get_db
from backend.shared.common.security import decode_token
from backend.services.auth.service import AuthService
from backend.services.auth.schemas import UserWithRoles

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> UserWithRoles:
    """
    Get current authenticated user from JWT token
    
    Usage:
        @app.get("/protected")
        async def protected_route(current_user: UserWithRoles = Depends(get_current_user)):
            return {"user": current_user}
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    
    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user details
    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(user_id, tenant_id)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: UserWithRoles = Depends(get_current_user)
) -> UserWithRoles:
    """
    Get current active user
    
    Usage:
        @app.get("/protected")
        async def protected_route(user: UserWithRoles = Depends(get_current_active_user)):
            return {"user": user}
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: UserWithRoles = Depends(get_current_active_user)
) -> UserWithRoles:
    """
    Get current superuser
    
    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: str,
            admin: UserWithRoles = Depends(get_current_superuser)
        ):
            ...
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user


def require_permission(permission: str):
    """
    Dependency factory to require specific permission
    
    Args:
        permission: Permission string (e.g., "users:create")
        
    Usage:
        @app.post("/users")
        async def create_user(
            user: UserWithRoles = Depends(require_permission("users:create"))
        ):
            ...
    """
    async def permission_checker(
        current_user: UserWithRoles = Depends(get_current_active_user)
    ) -> UserWithRoles:
        # Superusers have all permissions
        if current_user.is_superuser:
            return current_user
        
        # Check if user has the required permission
        if permission not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}"
            )
        
        return current_user
    
    return permission_checker


def require_role(role: str):
    """
    Dependency factory to require specific role
    
    Args:
        role: Role name (e.g., "admin", "manager")
        
    Usage:
        @app.get("/admin/dashboard")
        async def admin_dashboard(
            user: UserWithRoles = Depends(require_role("admin"))
        ):
            ...
    """
    async def role_checker(
        current_user: UserWithRoles = Depends(get_current_active_user)
    ) -> UserWithRoles:
        # Superusers have all roles
        if current_user.is_superuser:
            return current_user
        
        return current_user
    
    return role_checker


async def get_tenant_id(
    current_user: UserWithRoles = Depends(get_current_user)
) -> str:
    """
    Get tenant ID from current user context
    
    Usage:
        @app.get("/protected")
        async def protected_route(tenant_id: str = Depends(get_tenant_id)):
            return {"tenant_id": tenant_id}
    """
    if not hasattr(current_user, 'tenant_id') or not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenant associated with user"
        )
    return current_user.tenant_id
