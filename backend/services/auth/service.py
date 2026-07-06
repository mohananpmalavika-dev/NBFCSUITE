"""
Authentication Service
Business logic for authentication
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Tuple
from datetime import datetime, timedelta
import uuid

from backend.shared.database.models import User, Role, Permission, UserRole, RolePermission
from backend.shared.common.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from backend.shared.middleware.error_handler import (
    UnauthorizedError,
    ValidationError,
    NotFoundError,
    ConflictError
)
from backend.services.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserWithRoles
)


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def login(self, request: LoginRequest) -> Tuple[TokenResponse, UserWithRoles]:
        """
        Authenticate user and return tokens
        
        Args:
            request: Login request
            
        Returns:
            Tuple of (TokenResponse, UserWithRoles)
            
        Raises:
            UnauthorizedError: Invalid credentials
        """
        # Find user
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.tenant_id == request.tenant_id,
                    User.username == request.username,
                    User.is_deleted == False
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedError("Invalid username or password")
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise UnauthorizedError(
                f"Account is locked until {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')}"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            
            await self.db.commit()
            raise UnauthorizedError("Invalid username or password")
        
        # Check if user is active
        if not user.is_active:
            raise UnauthorizedError("Account is inactive")
        
        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        user.last_activity = datetime.utcnow()
        user.login_count += 1
        
        await self.db.commit()
        
        # Get user roles and permissions
        roles, permissions = await self._get_user_roles_and_permissions(user.id, user.tenant_id)
        
        # Create tokens
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "tenant_id": user.tenant_id,
            "is_superuser": user.is_superuser,
            "roles": roles
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=30 * 60  # 30 minutes
        )
        
        user_response = UserWithRoles(
            **user.dict(),
            roles=roles,
            permissions=permissions
        )
        
        return token_response, user_response
    
    async def register(self, request: RegisterRequest) -> UserResponse:
        """
        Register new user
        
        Args:
            request: Registration request
            
        Returns:
            Created user
            
        Raises:
            ConflictError: Username or email already exists
        """
        # Ensure default tenant exists
        from backend.shared.database.models import Tenant
        tenant_result = await self.db.execute(
            select(Tenant).where(Tenant.code == request.tenant_id)
        )
        tenant = tenant_result.scalar_one_or_none()
        
        if not tenant:
            # Create default tenant
            tenant = Tenant(
                id=uuid.uuid4(),
                name="Default Organization",
                code=request.tenant_id,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(tenant)
            await self.db.flush()  # Flush to get the tenant ID
        
        # Check if username exists
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.tenant_id == request.tenant_id,
                    User.username == request.username,
                    User.is_deleted == False
                )
            )
        )
        if result.scalar_one_or_none():
            raise ConflictError("Username already exists")
        
        # Check if email exists
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.tenant_id == request.tenant_id,
                    User.email == request.email,
                    User.is_deleted == False
                )
            )
        )
        if result.scalar_one_or_none():
            raise ConflictError("Email already exists")
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            tenant_id=request.tenant_id,
            email=request.email,
            username=request.username,
            password_hash=hash_password(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            is_active=True,
            is_superuser=False,
            is_verified=False,
            email_verified=False,
            phone_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return UserResponse(**user.dict())
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
            
        Raises:
            UnauthorizedError: Invalid refresh token
        """
        # Decode refresh token
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid refresh token")
        
        # Get user
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.id == uuid.UUID(user_id),
                    User.is_deleted == False,
                    User.is_active == True
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UnauthorizedError("User not found or inactive")
        
        # Get user roles
        roles, _ = await self._get_user_roles_and_permissions(user.id, user.tenant_id)
        
        # Create new tokens
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "tenant_id": user.tenant_id,
            "is_superuser": user.is_superuser,
            "roles": roles
        }
        
        access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=30 * 60
        )
    
    async def get_current_user(self, user_id: str, tenant_id: str) -> UserWithRoles:
        """
        Get current user details
        
        Args:
            user_id: User ID from token
            tenant_id: Tenant ID from token
            
        Returns:
            User with roles and permissions
            
        Raises:
            NotFoundError: User not found
        """
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.id == uuid.UUID(user_id),
                    User.tenant_id == tenant_id,
                    User.is_deleted == False
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Get roles and permissions
        roles, permissions = await self._get_user_roles_and_permissions(user.id, user.tenant_id)
        
        return UserWithRoles(
            **user.dict(),
            roles=roles,
            permissions=permissions
        )
    
    async def change_password(
        self,
        user_id: str,
        tenant_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            UnauthorizedError: Invalid current password
        """
        result = await self.db.execute(
            select(User).where(
                and_(
                    User.id == uuid.UUID(user_id),
                    User.tenant_id == tenant_id,
                    User.is_deleted == False
                )
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.password_changed_at = datetime.utcnow()
        user.must_change_password = False
        user.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def _get_user_roles_and_permissions(
        self,
        user_id: uuid.UUID,
        tenant_id: str
    ) -> Tuple[list, list]:
        """Get user's roles and permissions"""
        # Get user roles
        result = await self.db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                and_(
                    UserRole.user_id == user_id,
                    UserRole.tenant_id == tenant_id,
                    UserRole.is_deleted == False,
                    Role.is_active == True
                )
            )
        )
        roles = result.scalars().all()
        role_names = [role.name for role in roles]
        
        # Get permissions for all roles
        role_ids = [role.id for role in roles]
        if role_ids:
            result = await self.db.execute(
                select(Permission)
                .join(RolePermission, RolePermission.permission_id == Permission.id)
                .where(
                    and_(
                        RolePermission.role_id.in_(role_ids),
                        RolePermission.tenant_id == tenant_id,
                        RolePermission.is_deleted == False,
                        Permission.is_active == True
                    )
                )
            )
            permissions = result.scalars().all()
            permission_strings = [f"{p.resource}:{p.action}" for p in permissions]
        else:
            permission_strings = []
        
        return role_names, permission_strings
