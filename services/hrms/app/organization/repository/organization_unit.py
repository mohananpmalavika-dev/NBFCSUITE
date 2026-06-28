from typing import List, Optional
from uuid import uuid4

from sqlalchemy.orm import Session

from app.organization.models.organization_unit import OrganizationUnit


class OrganizationUnitRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: dict) -> OrganizationUnit:
        item = OrganizationUnit(id=str(uuid4()), **payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self, tenant_id: str, status: Optional[str] = None) -> List[OrganizationUnit]:
        query = self.db.query(OrganizationUnit).filter(OrganizationUnit.tenant_id == tenant_id)
        if status:
            query = query.filter(OrganizationUnit.status == status)
        return query.order_by(OrganizationUnit.display_order.asc(), OrganizationUnit.unit_name.asc()).all()

    def get_by_id(self, unit_id: str, tenant_id: str) -> Optional[OrganizationUnit]:
        return self.db.query(OrganizationUnit).filter(OrganizationUnit.id == unit_id, OrganizationUnit.tenant_id == tenant_id).first()

    def update(self, item: OrganizationUnit, payload: dict) -> OrganizationUnit:
        for key, value in payload.items():
            if value is not None:
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete(self, item: OrganizationUnit) -> None:
        self.db.delete(item)
        self.db.commit()
