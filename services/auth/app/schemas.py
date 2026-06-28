from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any


class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class Permission(PermissionBase):
    id: str

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permissions: Optional[List[str]] = None


class Role(RoleBase):
    id: str
    permissions: List[Permission] = []

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_id: Optional[str] = None
    access_branch_ids: Optional[List[str]] = None
    mfa_enabled: Optional[bool] = None
    mfa_method: Optional[str] = None


class UserCreate(UserBase):
    password: str
    roles: Optional[List[str]] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_id: Optional[str] = None
    access_branch_ids: Optional[List[str]] = None
    mfa_enabled: Optional[bool] = None
    mfa_method: Optional[str] = None
    roles: Optional[List[str]] = None


class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    roles: List[Role] = []
    permissions: List[str] = []
    groups: List["UserGroup"] = []
    access_branch_ids: Optional[List[str]] = None
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserSessionBase(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    ip_address: Optional[str] = None


class UserSession(UserSessionBase):
    id: str
    user_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class APIKeyBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tenant_id: Optional[str] = None
    expires_at: Optional[datetime] = None


class APIKeyCreate(APIKeyBase):
    pass


class APIKey(APIKeyBase):
    id: str
    user_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyResponse(APIKey):
    key: str


class UserGroupBase(BaseModel):
    name: str
    description: Optional[str] = None


class UserGroupCreate(UserGroupBase):
    pass


class UserGroup(UserGroupBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Resolve forward references for models using string annotations in Pydantic v2
User.model_rebuild()


class LoginHistoryBase(BaseModel):
    event_type: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: Optional[bool] = True
    details: Optional[Dict[str, Any]] = None


class LoginHistory(LoginHistoryBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogBase(BaseModel):
    action: str
    resource: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    tenant_id: Optional[str] = None


class AuditLog(AuditLogBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OTPRequest(BaseModel):
    user_id: str
    purpose: str


class OTPVerify(BaseModel):
    user_id: str
    code: str
    purpose: str


class AttributePolicyBase(BaseModel):
    resource_type: str
    action: str
    conditions: Optional[Dict[str, Any]] = None
    effect: Optional[str] = "allow"


class AttributePolicy(AttributePolicyBase):
    id: str
    tenant_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OAuthClientBase(BaseModel):
    name: str
    redirect_uris: Optional[List[str]] = None
    scopes: Optional[List[str]] = None


class OAuthClientCreate(OAuthClientBase):
    client_id: Optional[str] = None
    client_secret: Optional[str] = None


class OAuthClient(OAuthClientBase):
    id: str
    client_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OAuthClientResponse(OAuthClient):
    client_secret: str

    class Config:
        from_attributes = True


class OAuthAuthorizeRequest(BaseModel):
    client_id: str
    redirect_uri: str
    scope: Optional[List[str]] = None
    state: Optional[str] = None


class OAuthAuthorizeResponse(BaseModel):
    code: str
    redirect_uri: str
    state: Optional[str] = None
    expires_at: datetime


class OAuthTokenRequest(BaseModel):
    client_id: str
    client_secret: str
    code: str
    redirect_uri: str
    grant_type: str = "authorization_code"


class ExternalIdentityProviderBase(BaseModel):
    provider_type: str
    display_name: str
    configuration: Optional[dict] = None


class ExternalIdentityProviderCreate(ExternalIdentityProviderBase):
    pass


class ExternalIdentityProvider(ExternalIdentityProviderBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApprovalRuleBase(BaseModel):
    tenant_id: Optional[str] = None
    action: str
    required_roles: Optional[List[str]] = None
    threshold: Optional[str] = None
    enabled: Optional[bool] = True


class ApprovalRuleCreate(ApprovalRuleBase):
    pass


class ApprovalRule(ApprovalRuleBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    ip_address: Optional[str] = None


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
    permissions: List[str] = []
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    branch_id: Optional[str] = None


class TenantConfigurationBase(BaseModel):
    tenant_id: str
    display_name: str
    legal_name: Optional[str] = None
    primary_color: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[dict] = None


class TenantConfigurationCreate(TenantConfigurationBase):
    pass


class TenantConfiguration(TenantConfigurationBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
