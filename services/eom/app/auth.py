from fastapi import Header, HTTPException, Depends
from typing import List, Optional


def get_current_roles(x_user_roles: Optional[str] = Header(None)) -> List[str]:
    # Accept roles in header `X-User-Roles: role1,role2` for dev/testing
    if not x_user_roles:
        return []
    return [r.strip() for r in x_user_roles.split(',') if r.strip()]


def require_role(role: str):
    def _dep(roles: List[str] = Depends(get_current_roles)):
        if role not in roles:
            raise HTTPException(status_code=403, detail='forbidden')
        return True
    return _dep
