from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.organization.models.organization_unit import OrganizationUnit
from app.organization.repository.organization_unit import OrganizationUnitRepository
from app.organization.schemas.organization_unit import (
    OrganizationAnalyticsResponse,
    OrganizationUnitCreate,
    OrganizationUnitTreeResponse,
    OrganizationUnitUpdate,
)


class OrganizationUnitService:
    def __init__(self, db: Session):
        self.repo = OrganizationUnitRepository(db)
        self.db = db

    def create(self, payload: OrganizationUnitCreate, changed_by: Optional[str] = None) -> OrganizationUnit:
        self._validate_unique_code(payload.tenant_id, payload.unit_code, payload.parent_id)
        item = self.repo.create(payload.model_dump())
        self.repo.create_closure_entries(item)
        self.repo.record_audit("create", item, changed_by=changed_by)
        return item

    def list(self, tenant_id: str, status: Optional[str] = None) -> List[OrganizationUnit]:
        return self.repo.list(tenant_id=tenant_id, status=status)

    def get(self, unit_id: str, tenant_id: str) -> OrganizationUnit:
        item = self.repo.get_by_id(unit_id, tenant_id)
        if not item:
            raise HTTPException(status_code=404, detail="Organization unit not found")
        return item

    def update(self, unit_id: str, tenant_id: str, payload: OrganizationUnitUpdate, changed_by: Optional[str] = None) -> OrganizationUnit:
        item = self.get(unit_id, tenant_id)
        update_payload = payload.model_dump(exclude_unset=True)
        if update_payload.get("unit_code"):
            self._validate_unique_code(tenant_id, update_payload["unit_code"], update_payload.get("parent_id"), current_id=unit_id)
        updated = self.repo.update(item, update_payload)
        if "parent_id" in update_payload:
            self.repo.rebuild_closure_entries(updated)
        self.repo.record_audit("update", updated, changed_by=changed_by, data=update_payload)
        return updated

    def delete(self, unit_id: str, tenant_id: str, changed_by: Optional[str] = None) -> None:
        item = self.get(unit_id, tenant_id)
        if self.repo.has_children(item):
            raise HTTPException(status_code=400, detail="Cannot delete organization unit with child units")
        self.repo.delete_closure_entries(item)
        self.repo.record_audit("delete", item, changed_by=changed_by)
        self.repo.delete(item)

    def tree(self, tenant_id: str) -> List[OrganizationUnitTreeResponse]:
        items = self.repo.list(tenant_id=tenant_id)
        by_id = {item.id: item for item in items}
        roots = [item for item in items if not item.parent_id]
        result = []
        for item in roots:
            result.append(self._build_tree(item, by_id))
        return result

    def analytics(self, tenant_id: str) -> OrganizationAnalyticsResponse:
        items = self.repo.list(tenant_id=tenant_id)
        by_type: Dict[str, int] = {}
        for item in items:
            by_type[item.unit_type] = by_type.get(item.unit_type, 0) + 1
        return OrganizationAnalyticsResponse(
            total_units=len(items),
            active_units=sum(1 for item in items if item.status == "active"),
            inactive_units=sum(1 for item in items if item.status != "active"),
            by_type=by_type,
        )

    def _build_tree(self, item: OrganizationUnit, by_id: Dict[str, OrganizationUnit]) -> OrganizationUnitTreeResponse:
        children = [self._build_tree(child, by_id) for child in self.repo.list(item.tenant_id, status=None) if child.parent_id == item.id]
        return OrganizationUnitTreeResponse(
            id=item.id,
            tenant_id=item.tenant_id,
            parent_id=item.parent_id,
            unit_code=item.unit_code,
            unit_name=item.unit_name,
            unit_type=item.unit_type,
            display_order=item.display_order,
            status=item.status,
            effective_from=item.effective_from,
            effective_to=item.effective_to,
            manager_position_id=item.manager_position_id,
            cost_center_id=item.cost_center_id,
            profit_center_id=item.profit_center_id,
            address_id=item.address_id,
            created_at=item.created_at,
            updated_at=item.updated_at,
            children=children,
        )

    def _validate_unique_code(self, tenant_id: str, unit_code: str, parent_id: Optional[str], current_id: Optional[str] = None) -> None:
        existing = self.db.query(OrganizationUnit).filter(
            OrganizationUnit.tenant_id == tenant_id,
            OrganizationUnit.unit_code == unit_code,
            OrganizationUnit.parent_id == parent_id,
        )
        if current_id:
            existing = existing.filter(OrganizationUnit.id != current_id)
        if existing.first():
            raise HTTPException(status_code=400, detail="Organization unit code already exists in this parent scope")
