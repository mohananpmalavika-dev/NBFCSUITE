from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.organization.schemas.organization_unit import (
    OrganizationAnalyticsResponse,
    OrganizationUnitCreate,
    OrganizationUnitResponse,
    OrganizationUnitTreeResponse,
    OrganizationUnitUpdate,
)
from app.organization.services.organization_unit import OrganizationUnitService
from app.security import get_current_user_claims

router = APIRouter(prefix="/organization", tags=["organization"])


@router.post("/unit", response_model=OrganizationUnitResponse)
def create_organization_unit(
    payload: OrganizationUnitCreate,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    tenant_id = payload.tenant_id or claims.get("tenant_id") or "default"
    service = OrganizationUnitService(db)
    return service.create(
        OrganizationUnitCreate(**{**payload.model_dump(), "tenant_id": tenant_id}),
        changed_by=claims.get("user_id"),
    )


@router.get("/tree", response_model=List[OrganizationUnitTreeResponse])
def get_organization_tree(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    tenant_id = claims.get("tenant_id") or "default"
    return OrganizationUnitService(db).tree(tenant_id)


@router.put("/unit/{unit_id}", response_model=OrganizationUnitResponse)
def update_organization_unit(
    unit_id: str,
    payload: OrganizationUnitUpdate,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    tenant_id = claims.get("tenant_id") or "default"
    return OrganizationUnitService(db).update(unit_id, tenant_id, payload, changed_by=claims.get("user_id"))


@router.delete("/unit/{unit_id}")
def delete_organization_unit(
    unit_id: str,
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    tenant_id = claims.get("tenant_id") or "default"
    OrganizationUnitService(db).delete(unit_id, tenant_id, changed_by=claims.get("user_id"))
    return {"message": "Organization unit deleted"}


@router.get("/chart")
def get_organization_chart(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    tenant_id = claims.get("tenant_id") or "default"
    return {"tenant_id": tenant_id, "items": OrganizationUnitService(db).list(tenant_id)}


@router.get("/search")
def search_organization_units(
    q: str = Query(default=""),
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    tenant_id = claims.get("tenant_id") or "default"
    service = OrganizationUnitService(db)
    items = service.list(tenant_id)
    filtered = [item for item in items if q.lower() in item.unit_name.lower() or q.lower() in item.unit_code.lower()]
    return filtered


@router.get("/analytics", response_model=OrganizationAnalyticsResponse)
def get_organization_analytics(
    db: Session = Depends(get_db),
    claims: dict = Depends(get_current_user_claims),
):
    tenant_id = claims.get("tenant_id") or "default"
    return OrganizationUnitService(db).analytics(tenant_id)
