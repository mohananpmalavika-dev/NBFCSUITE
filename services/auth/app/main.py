from fastapi import FastAPI, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, List

from app.config import settings
from app.database import get_db, init_db
from app.models import (
    User,
    Role,
    Permission,
    UserSession,
    APIKey,
    OAuthClient,
    ExternalIdentityProvider,
    ApprovalRule,
    TenantConfiguration,
)
from app.schemas import (
    UserCreate,
    User as UserSchema,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    RoleCreate,
    Role as RoleSchema,
    PermissionCreate,
    Permission as PermissionSchema,
    RefreshTokenRequest,
    TokenValidationResponse,
    UserSession as UserSessionSchema,
    APIKeyCreate,
    APIKeyResponse,
    OAuthClientCreate,
    OAuthClient as OAuthClientSchema,
    OAuthClientResponse,
    ExternalIdentityProviderCreate,
    ExternalIdentityProvider as ExternalIdentityProviderSchema,
    ApprovalRuleCreate,
    ApprovalRule as ApprovalRuleSchema,
    TenantConfigurationCreate,
    TenantConfiguration as TenantConfigurationSchema,
)
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    hash_secret,
    verify_secret,
    generate_secret,
)

app = FastAPI(title="auth-service", version="0.1.0")


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    return authorization.split(" ", 1)[1]


def _extract_api_key(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("apikey "):
        return authorization.split(" ", 1)[1]
    return None


def _collect_permissions(user: User) -> list[str]:
    permissions = {permission.name for role in user.roles for permission in role.permissions}
    return sorted(permissions)


def _token_payload(user: User, token_type: str = "access") -> dict:
    return {
        "sub": user.id,
        "username": user.username,
        "roles": [role.name for role in user.roles],
        "permissions": _collect_permissions(user),
        "typ": token_type,
        "tenant_id": user.tenant_id,
        "organization_id": user.organization_id,
        "zone_id": user.zone_id,
        "region_id": user.region_id,
        "area_id": user.area_id,
        "branch_id": user.branch_id,
    }


def require_role(role_name: str):
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if role_name not in [role.name for role in current_user.roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must have '{role_name}' role",
            )
        return current_user
    return role_dependency


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    if authorization.lower().startswith("bearer "):
        token = _extract_bearer_token(authorization)
        payload = decode_token(token)
        if not payload or payload.get("typ") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        user = db.query(User).filter(User.id == payload.get("sub")).first()
    elif authorization.lower().startswith("apikey "):
        api_key_value = _extract_api_key(authorization)
        if not api_key_value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key missing",
            )
        api_keys = db.query(APIKey).filter(APIKey.is_active == True).all()
        user = None
        for candidate in api_keys:
            if verify_secret(api_key_value, candidate.key_hash):
                user = db.query(User).filter(User.id == candidate.user_id).first()
                break
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unsupported authorization scheme",
        )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


@app.on_event("startup")
async def startup():
    """Initialize database on startup and seed core IAM artifacts."""
    init_db()
    db = next(get_db())

    default_roles = [
        {"name": "admin", "description": "Administrator"},
        {"name": "user", "description": "Regular User"},
        {"name": "lender", "description": "Lender/Officer"},
        {"name": "collector", "description": "Collections Officer"},
        {"name": "branch_manager", "description": "Branch Manager"},
        {"name": "regional_manager", "description": "Regional Manager"},
    ]
    for role_data in default_roles:
        if not db.query(Role).filter(Role.name == role_data["name"]).first():
            db.add(Role(**role_data))

    default_permissions = [
        {"name": "view_customer", "description": "View customer profile"},
        {"name": "edit_customer", "description": "Edit customer profile"},
        {"name": "create_application", "description": "Create loan application"},
        {"name": "approve_application", "description": "Approve loan application"},
        {"name": "reject_application", "description": "Reject loan application"},
        {"name": "view_loan", "description": "View loan details"},
        {"name": "collect_payment", "description": "Collect payment"},
        {"name": "manage_collections", "description": "Manage collections workflow"},
    ]
    for perm_data in default_permissions:
        if not db.query(Permission).filter(Permission.name == perm_data["name"]).first():
            db.add(Permission(**perm_data))

    db.commit()

    admin_role = db.query(Role).filter(Role.name == "admin").first()
    all_permissions = db.query(Permission).all()
    if admin_role:
        admin_role.permissions = all_permissions

    if not db.query(User).filter(User.username == "admin").first():
        admin = User(
            username="admin",
            email="admin@nbfcsuite.local",
            hashed_password=hash_password("admin123"),
            is_active=True,
            tenant_id="default",
        )
        if admin_role:
            admin.roles.append(admin_role)
        db.add(admin)

    db.commit()
    db.close()


@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - exchange credentials for JWT token."""
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )

    access_token = create_access_token(data=_token_payload(user, "access"))
    refresh_token = create_access_token(
        data=_token_payload(user, "refresh"),
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_secret(refresh_token),
        device_name=credentials.device_name,
        device_type=credentials.device_type,
        ip_address=credentials.ip_address,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        last_used_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(session)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("typ") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = db.query(User).filter(User.id == decoded.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    session = None
    for session_candidate in db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True,
    ).all():
        if verify_secret(payload.refresh_token, session_candidate.refresh_token_hash):
            session = session_candidate
            break

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session not found or has been revoked",
        )

    access_token = create_access_token(data=_token_payload(user, "access"))
    refresh_token = create_access_token(
        data=_token_payload(user, "refresh"),
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )

    session.refresh_token_hash = hash_secret(refresh_token)
    session.last_used_at = datetime.utcnow()
    session.expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@app.get("/auth/validate", response_model=TokenValidationResponse)
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate the bearer token and return the authenticated principal."""
    return TokenValidationResponse(
        valid=True,
        user_id=current_user.id,
        username=current_user.username,
        roles=[role.name for role in current_user.roles],
        permissions=_collect_permissions(current_user),
        tenant_id=current_user.tenant_id,
        organization_id=current_user.organization_id,
        zone_id=current_user.zone_id,
        region_id=current_user.region_id,
        area_id=current_user.area_id,
        branch_id=current_user.branch_id,
    )


@app.get("/auth/users/me", response_model=UserSchema)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@app.get("/auth/users", response_model=list[UserSchema])
async def list_users(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/auth/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.id != user.id and "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user")
    return user


@app.post("/auth/roles", response_model=RoleSchema)
async def create_role(role_data: RoleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    if db.query(Role).filter(Role.name == role_data.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")

    role = Role(name=role_data.name, description=role_data.description)
    if role_data.permissions:
        permissions = db.query(Permission).filter(Permission.name.in_(role_data.permissions)).all()
        if len(permissions) != len(role_data.permissions):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more permissions do not exist",
            )
        role.permissions.extend(permissions)

    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@app.get("/auth/roles", response_model=list[RoleSchema])
async def list_roles(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Role).all()


@app.get("/auth/roles/{role_id}", response_model=RoleSchema)
async def get_role(role_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@app.post("/auth/users", response_model=UserSchema)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        is_active=True,
        tenant_id=user_data.tenant_id,
        organization_id=user_data.organization_id,
        zone_id=user_data.zone_id,
        region_id=user_data.region_id,
        area_id=user_data.area_id,
        branch_id=user_data.branch_id,
    )

    if hasattr(user_data, "roles") and user_data.roles:
        assigned_roles = db.query(Role).filter(Role.name.in_(user_data.roles)).all()
        if len(assigned_roles) != len(user_data.roles):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more roles do not exist",
            )
        new_user.roles.extend(assigned_roles)
    else:
        default_role = db.query(Role).filter(Role.name == "user").first()
        if default_role:
            new_user.roles.append(default_role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.put("/auth/users/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != user.id and "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    if payload.email is not None:
        user.email = payload.email
    if payload.password:
        user.hashed_password = hash_password(payload.password)
    if payload.tenant_id is not None:
        user.tenant_id = payload.tenant_id
    if payload.organization_id is not None:
        user.organization_id = payload.organization_id
    if payload.zone_id is not None:
        user.zone_id = payload.zone_id
    if payload.region_id is not None:
        user.region_id = payload.region_id
    if payload.area_id is not None:
        user.area_id = payload.area_id
    if payload.branch_id is not None:
        user.branch_id = payload.branch_id
    if payload.roles is not None:
        if "admin" not in [role.name for role in current_user.roles] and current_user.id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to assign roles")
        assigned_roles = db.query(Role).filter(Role.name.in_(payload.roles)).all()
        if len(assigned_roles) != len(payload.roles):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more roles do not exist",
            )
        user.roles = assigned_roles

    db.commit()
    db.refresh(user)
    return user


@app.delete("/auth/users/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != user.id and "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to deactivate this user")

    user.is_active = False
    db.commit()
    return {"detail": "User deactivated"}


@app.get("/auth/users/{user_id}/roles", response_model=list[RoleSchema])
async def list_user_roles(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if current_user.id != user.id and "admin" not in [role.name for role in current_user.roles]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view roles for this user")
    return user.roles


@app.post("/auth/permissions", response_model=PermissionSchema)
async def create_permission(permission_data: PermissionCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    existing_permission = db.query(Permission).filter(Permission.name == permission_data.name).first()
    if existing_permission:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission already exists")
    new_permission = Permission(name=permission_data.name, description=permission_data.description)
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    return new_permission


@app.get("/auth/permissions", response_model=list[PermissionSchema])
async def list_permissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Permission).all()


@app.get("/auth/permissions/{permission_id}", response_model=PermissionSchema)
async def get_permission(permission_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")
    return permission


@app.post("/auth/roles/{role_id}/permissions", response_model=RoleSchema)
async def add_permission_to_role(role_id: str, permission_data: PermissionCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    permission = db.query(Permission).filter(Permission.name == permission_data.name).first()
    if not permission:
        permission = Permission(name=permission_data.name, description=permission_data.description)
        db.add(permission)
        db.commit()
        db.refresh(permission)

    if permission not in role.permissions:
        role.permissions.append(permission)
        db.commit()
        db.refresh(role)

    return role


@app.delete("/auth/roles/{role_id}/permissions/{permission_id}", response_model=RoleSchema)
async def remove_permission_from_role(role_id: str, permission_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission or permission not in role.permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not assigned to role")

    role.permissions.remove(permission)
    db.commit()
    db.refresh(role)
    return role


@app.get("/auth/sessions", response_model=list[UserSessionSchema])
async def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(UserSession).filter(UserSession.user_id == current_user.id).all()


@app.delete("/auth/sessions/{session_id}")
async def revoke_session(session_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.id == session_id, UserSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    session.is_active = False
    db.commit()
    return {"detail": "Session revoked"}


@app.post("/auth/keys", response_model=APIKeyResponse)
async def create_api_key(payload: APIKeyCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    raw_key = generate_secret(32)
    api_key = APIKey(
        user_id=current_user.id,
        key_hash=hash_secret(raw_key),
        name=payload.name,
        description=payload.description,
        tenant_id=payload.tenant_id or current_user.tenant_id,
        expires_at=payload.expires_at,
        is_active=True,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return APIKeyResponse(
        id=api_key.id,
        user_id=api_key.user_id,
        name=api_key.name,
        description=api_key.description,
        tenant_id=api_key.tenant_id,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        is_active=api_key.is_active,
        key=raw_key,
    )


@app.get("/auth/keys", response_model=list[APIKeyResponse])
async def list_api_keys(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return [
        APIKeyResponse(
            id=key.id,
            user_id=key.user_id,
            name=key.name,
            description=key.description,
            tenant_id=key.tenant_id,
            created_at=key.created_at,
            expires_at=key.expires_at,
            is_active=key.is_active,
            key="",
        )
        for key in keys
    ]


@app.delete("/auth/keys/{key_id}")
async def revoke_api_key(key_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    api_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")
    api_key.is_active = False
    db.commit()
    return {"detail": "API key revoked"}


@app.post("/auth/oauth/clients", response_model=OAuthClientResponse)
async def create_oauth_client(payload: OAuthClientCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    client_id = payload.client_id or generate_secret(16)
    client_secret = payload.client_secret or generate_secret(32)
    client = OAuthClient(
        client_id=client_id,
        client_secret_hash=hash_secret(client_secret),
        name=payload.name,
        redirect_uris=payload.redirect_uris,
        scopes=payload.scopes,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return OAuthClientResponse(
        id=client.id,
        client_id=client.client_id,
        name=client.name,
        redirect_uris=client.redirect_uris,
        scopes=client.scopes,
        is_active=client.is_active,
        created_at=client.created_at,
        client_secret=client_secret,
    )


@app.get("/auth/oauth/clients", response_model=list[OAuthClientSchema])
async def list_oauth_clients(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return db.query(OAuthClient).all()


@app.post("/auth/external-providers", response_model=ExternalIdentityProviderSchema)
async def create_external_provider(payload: ExternalIdentityProviderCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    provider = ExternalIdentityProvider(
        provider_type=payload.provider_type,
        display_name=payload.display_name,
        configuration=payload.configuration,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@app.get("/auth/external-providers", response_model=list[ExternalIdentityProviderSchema])
async def list_external_providers(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return db.query(ExternalIdentityProvider).all()


@app.post("/auth/approval-rules", response_model=ApprovalRuleSchema)
async def create_approval_rule(payload: ApprovalRuleCreate, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    rule = ApprovalRule(
        tenant_id=payload.tenant_id,
        action=payload.action,
        required_roles=payload.required_roles,
        threshold=payload.threshold,
        enabled=payload.enabled if payload.enabled is not None else True,
        created_at=datetime.utcnow(),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@app.get("/auth/approval-rules", response_model=list[ApprovalRuleSchema])
async def list_approval_rules(current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    return db.query(ApprovalRule).all()


@app.get("/auth/approval-rules/{rule_id}", response_model=ApprovalRuleSchema)
async def get_approval_rule(rule_id: str, current_user: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    rule = db.query(ApprovalRule).filter(ApprovalRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval rule not found")
    return rule


@app.post("/tenants/configurations", response_model=TenantConfigurationSchema, status_code=201)
async def create_tenant_configuration(
    payload: TenantConfigurationCreate,
    db: Session = Depends(get_db),
):
    """Create or update MVP tenant branding/configuration."""
    existing = (
        db.query(TenantConfiguration)
        .filter(TenantConfiguration.tenant_id == payload.tenant_id)
        .first()
    )
    if existing:
        existing.display_name = payload.display_name
        existing.legal_name = payload.legal_name
        existing.primary_color = payload.primary_color
        existing.logo_url = payload.logo_url
        existing.settings = payload.settings
        db.commit()
        db.refresh(existing)
        return existing

    tenant_config = TenantConfiguration(
        tenant_id=payload.tenant_id,
        display_name=payload.display_name,
        legal_name=payload.legal_name,
        primary_color=payload.primary_color,
        logo_url=payload.logo_url,
        settings=payload.settings,
    )
    db.add(tenant_config)
    db.commit()
    db.refresh(tenant_config)
    return tenant_config


@app.get("/tenants/configurations/{tenant_id}", response_model=TenantConfigurationSchema)
async def get_tenant_configuration(tenant_id: str, db: Session = Depends(get_db)):
    tenant_config = (
        db.query(TenantConfiguration)
        .filter(TenantConfiguration.tenant_id == tenant_id)
        .first()
    )
    if not tenant_config:
        raise HTTPException(status_code=404, detail="Tenant configuration not found")
    return tenant_config


@app.get("/")
async def root():
    return {"service": "auth", "version": "0.1.0"}
