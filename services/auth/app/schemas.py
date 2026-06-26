from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: str
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    roles: List[Role] = []
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenValidationResponse(BaseModel):
    valid: bool
    user_id: str
    username: str
    roles: List[str] = []
