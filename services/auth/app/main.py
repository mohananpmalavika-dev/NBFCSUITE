from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db, init_db
from app.models import User, Role
from app.schemas import (
    UserCreate, User as UserSchema, LoginRequest, TokenResponse, 
    RoleCreate, Role as RoleSchema
)
from app.security import hash_password, verify_password, create_access_token

app = FastAPI(title="auth-service", version="0.1.0")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    # Create sample roles if they don't exist
    db = next(get_db())
    if db.query(Role).count() == 0:
        admin_role = Role(name="admin", description="Administrator")
        user_role = Role(name="user", description="Regular User")
        lender_role = Role(name="lender", description="Lender/Officer")
        collector_role = Role(name="collector", description="Collections Officer")
        db.add_all([admin_role, user_role, lender_role, collector_role])
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
    
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username}
    )
    
    return TokenResponse(access_token=access_token)


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
        is_active=True
    )
    
    # Assign default 'user' role
    default_role = db.query(Role).filter(Role.name == "user").first()
    if default_role:
        new_user.roles.append(default_role)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


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
async def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List all users (with pagination)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


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


@app.get("/")
async def root():
    return {"service": "auth", "version": "0.1.0"}
