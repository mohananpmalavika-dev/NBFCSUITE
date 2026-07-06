"""
Authentication Router
API endpoints for authentication
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    ChangePasswordRequest,
    UserResponse,
    UserWithRoles
)
from backend.services.auth.service import AuthService
from backend.services.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account"
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: Valid email address
    - **username**: Unique username (3-50 characters)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **phone**: Optional phone number
    - **tenant_id**: Optional tenant ID (defaults to 'default')
    """
    auth_service = AuthService(db)
    user = await auth_service.register(request)
    
    return success_response(
        data=user.model_dump(mode='json'),
        message="User registered successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.post(
    "/login",
    response_model=dict,
    summary="User login",
    description="Authenticate user and get JWT tokens"
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return access and refresh tokens
    
    - **username**: Username
    - **password**: User password
    - **tenant_id**: Optional tenant ID (defaults to 'default')
    
    Returns:
    - **access_token**: JWT access token (expires in 30 minutes)
    - **refresh_token**: JWT refresh token (expires in 7 days)
    - **user**: User details with roles and permissions
    """
    auth_service = AuthService(db)
    tokens, user = await auth_service.login(request)
    
    return success_response(
        data={
            "tokens": tokens.model_dump(mode='json'),
            "user": user.model_dump(mode='json')
        },
        message="Login successful"
    )


@router.post(
    "/refresh",
    response_model=dict,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access and refresh tokens
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(request.refresh_token)
    
    return success_response(
        data=tokens.model_dump(mode='json'),
        message="Token refreshed successfully"
    )


@router.get(
    "/me",
    response_model=dict,
    summary="Get current user",
    description="Get details of currently authenticated user"
)
async def get_me(
    current_user: UserWithRoles = Depends(get_current_active_user)
):
    """
    Get current user details
    
    Requires: Valid access token in Authorization header
    
    Returns user details with roles and permissions
    """
    return success_response(
        data=current_user.model_dump(mode='json'),
        message="User retrieved successfully"
    )


@router.post(
    "/change-password",
    response_model=dict,
    summary="Change password",
    description="Change password for current user"
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: UserWithRoles = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 characters)
    
    Requires: Valid access token
    """
    auth_service = AuthService(db)
    await auth_service.change_password(
        str(current_user.id),
        current_user.tenant_id,
        request.current_password,
        request.new_password
    )
    
    return success_response(
        message="Password changed successfully"
    )


@router.post(
    "/logout",
    response_model=dict,
    summary="Logout",
    description="Logout current user"
)
async def logout(
    current_user: UserWithRoles = Depends(get_current_active_user)
):
    """
    Logout user
    
    Note: Since we're using JWT tokens (stateless), this endpoint
    is mainly for client-side token removal. The token will still
    be valid until it expires.
    
    For production, consider implementing token blacklisting.
    """
    return success_response(
        message="Logged out successfully"
    )
