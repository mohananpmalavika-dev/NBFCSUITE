from fastapi import FastAPI, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db, init_db
from app.models import User, Role, TenantConfiguration
from app.schemas import (
    UserCreate, User as UserSchema, LoginRequest, TokenResponse, 
    RoleCreate, Role as RoleSchema, RefreshTokenRequest, TokenValidationResponse,
    TenantConfigurationCreate, TenantConfiguration as TenantConfigurationSchema,
)
from app.security import hash_password, verify_password, create_access_token, decode_token

app = FastAPI(title="auth-service", version="0.1.0")


def _token_payload(user: User, token_type: str = "access") -> dict:
    return {
        "sub": user.id,
        "username": user.username,
        "roles": [role.name for role in user.roles],
        "typ": token_type,
        "tenant_id": user.tenant_id,
        "organization_id": user.organization_id,
        "zone_id": user.zone_id,
        "region_id": user.region_id,
        "area_id": user.area_id,
        "branch_id": user.branch_id,
    }


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    return authorization.split(" ", 1)[1]


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer_token(authorization)
    payload = decode_token(token)
    if not payload or payload.get("typ") == "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    # Create sample roles if they don't exist
    db = next(get_db())
    if db.query(Role).count() == 0:
        roles = [
            Role(name="admin", description="Administrator"),
            Role(name="user", description="Regular User"),
            Role(name="lender", description="Lender/Officer"),
            Role(name="collector", description="Collections Officer"),
            Role(name="branch_manager", description="Branch Manager"),
            Role(name="regional_manager", description="Regional Manager"),
        ]
        db.add_all(roles)
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
        expires_delta=timedelta(days=7),
    )
    
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

    access_token = create_access_token(data=_token_payload(user, "access"))
    return TokenResponse(access_token=access_token, refresh_token=payload.refresh_token)


@app.get("/auth/validate", response_model=TokenValidationResponse)
async def validate_token(current_user: User = Depends(get_current_user)):
    """Validate the bearer token and return the authenticated principal."""
    return TokenValidationResponse(
        valid=True,
        user_id=current_user.id,
        username=current_user.username,
        roles=[role.name for role in current_user.roles],
        tenant_id=current_user.tenant_id,
        organization_id=current_user.organization_id,
        zone_id=current_user.zone_id,
        region_id=current_user.region_id,
        area_id=current_user.area_id,
        branch_id=current_user.branch_id,
    )


@app.post("/auth/users", response_model=UserSchema)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create user
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
    
    # Assign default 'user' role
    default_role = db.query(Role).filter(Role.name == "user").first()
    if default_role:
        new_user.roles.append(default_role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@app.get("/auth/users/me", response_model=UserSchema)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    return current_user


@app.get("/auth/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user profile by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@app.get("/auth/users", response_model=list[UserSchema])
async def list_users(
    tenant_id: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List all users (with pagination)."""
    query = db.query(User)
    if tenant_id:
        query = query.filter(User.tenant_id == tenant_id)
    return query.offset(skip).limit(limit).all()


@app.post("/auth/roles", response_model=RoleSchema)
async def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    """Create a new role."""
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role already exists"
        )
    
    new_role = Role(name=role_data.name, description=role_data.description)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return new_role


@app.get("/auth/roles", response_model=list[RoleSchema])
async def list_roles(db: Session = Depends(get_db)):
    """List all roles."""
    roles = db.query(Role).all()
    return roles


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
