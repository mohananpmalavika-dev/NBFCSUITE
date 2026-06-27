from typing import Optional

from fastapi import Header, HTTPException, status


def get_current_user_claims(
    tenant_id: Optional[str] = Header(default=None, alias="X-Tenant-Id"),
    user_id: Optional[str] = Header(default=None, alias="X-User-Id"),
    scope_organization_id: Optional[str] = Header(default=None, alias="X-Scope-Organization-Id"),
    legacy_organization_id: Optional[str] = Header(default=None, alias="X-Organization-Id"),
    scope_zone_id: Optional[str] = Header(default=None, alias="X-Scope-Zone-Id"),
    legacy_zone_id: Optional[str] = Header(default=None, alias="X-Zone-Id"),
    scope_region_id: Optional[str] = Header(default=None, alias="X-Scope-Region-Id"),
    legacy_region_id: Optional[str] = Header(default=None, alias="X-Region-Id"),
    scope_area_id: Optional[str] = Header(default=None, alias="X-Scope-Area-Id"),
    legacy_area_id: Optional[str] = Header(default=None, alias="X-Area-Id"),
    scope_branch_id: Optional[str] = Header(default=None, alias="X-Scope-Branch-Id"),
    legacy_branch_id: Optional[str] = Header(default=None, alias="X-Branch-Id"),
) -> dict:
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing tenant context. Provide X-Tenant-Id with the request.",
        )

    return {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "organization_id": scope_organization_id or legacy_organization_id,
        "zone_id": scope_zone_id or legacy_zone_id,
        "region_id": scope_region_id or legacy_region_id,
        "area_id": scope_area_id or legacy_area_id,
        "branch_id": scope_branch_id or legacy_branch_id,
    }


def scope_filter_columns(claims: dict) -> dict:
    """Return the scope filters to apply for HRMS data access."""
    return {
        key: value
        for key, value in {
            "tenant_id": claims.get("tenant_id"),
            "branch_id": claims.get("branch_id"),
            "area_id": claims.get("area_id"),
            "region_id": claims.get("region_id"),
            "zone_id": claims.get("zone_id"),
            "organization_id": claims.get("organization_id"),
        }.items()
        if value is not None
    }

