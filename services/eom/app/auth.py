from fastapi import Header, HTTPException, Depends, Request
from typing import List, Optional
import os
import jwt


def _roles_from_header(x_user_roles: Optional[str]) -> List[str]:
    if not x_user_roles:
        return []
    return [r.strip() for r in x_user_roles.split(',') if r.strip()]


def _roles_from_jwt(token: str) -> List[str]:
    # Try to decode JWT and read `roles` claim. Uses HMAC secret by default,
    # or a public key if `EOM_JWT_PUBLIC_KEY` is provided.
    secret = os.getenv('EOM_JWT_SECRET')
    pubkey = os.getenv('EOM_JWT_PUBLIC_KEY')
    try:
        if pubkey:
            payload = jwt.decode(token, pubkey, algorithms=['RS256'])
        elif secret:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
        else:
            return []
    except Exception:
        return []
    roles = payload.get('roles') or payload.get('role') or payload.get('permissions')
    if isinstance(roles, str):
        return [r.strip() for r in roles.split(',') if r.strip()]
    if isinstance(roles, list):
        return [str(r) for r in roles]
    return []


def get_current_roles(request: Request, x_user_roles: Optional[str] = Header(None)) -> List[str]:
    # Priority: JWT Authorization header (production), then X-User-Roles header (dev)
    auth = request.headers.get('authorization') or request.headers.get('Authorization')
    if auth and auth.lower().startswith('bearer '):
        token = auth.split(' ', 1)[1].strip()
        jwt_roles = _roles_from_jwt(token)
        if jwt_roles:
            return jwt_roles
    # fallback to header-based roles for development and tests
    return _roles_from_header(x_user_roles)


def require_role(role: str):
    def _dep(roles: List[str] = Depends(get_current_roles)):
        if role not in roles:
            raise HTTPException(status_code=403, detail='forbidden')
        return True
    return _dep
