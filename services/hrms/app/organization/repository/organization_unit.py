from typing import List, Optional
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.organization.models.organization_unit import OrganizationUnit
from app.organization.models.organization_unit_audit import OrganizationUnitAudit
from app.organization.models.organization_unit_closure import OrganizationUnitClosure


class OrganizationUnitRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: dict) -> OrganizationUnit:
        item = OrganizationUnit(id=str(uuid4()), **payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def create_closure_entries(self, item: OrganizationUnit) -> None:
        entries = []
        if item.parent_id:
            ancestor_rows = (
                self.db.query(OrganizationUnitClosure)
                .filter(
                    OrganizationUnitClosure.tenant_id == item.tenant_id,
                    OrganizationUnitClosure.descendant_id == item.parent_id,
                )
                .all()
            )
            for ancestor in ancestor_rows:
                entries.append(
                    OrganizationUnitClosure(
                        id=str(uuid4()),
                        tenant_id=item.tenant_id,
                        ancestor_id=ancestor.ancestor_id,
                        descendant_id=item.id,
                        depth=ancestor.depth + 1,
                    )
                )
        entries.append(
            OrganizationUnitClosure(
                id=str(uuid4()),
                tenant_id=item.tenant_id,
                ancestor_id=item.id,
                descendant_id=item.id,
                depth=0,
            )
        )
        self.db.add_all(entries)
        self.db.commit()

    def delete_closure_entries(self, item: OrganizationUnit) -> None:
        self.db.query(OrganizationUnitClosure).filter(
            OrganizationUnitClosure.tenant_id == item.tenant_id,
            or_(
                OrganizationUnitClosure.ancestor_id == item.id,
                OrganizationUnitClosure.descendant_id == item.id,
            ),
        ).delete(synchronize_session=False)
        self.db.commit()

    def has_children(self, item: OrganizationUnit) -> bool:
        return (
            self.db.query(OrganizationUnit)
            .filter(OrganizationUnit.parent_id == item.id, OrganizationUnit.tenant_id == item.tenant_id)
            .first()
            is not None
        )

    def descendants(self, item: OrganizationUnit) -> List[OrganizationUnit]:
        descendant_ids = [
            row.descendant_id
            for row in self.db.query(OrganizationUnitClosure)
            .filter(
                OrganizationUnitClosure.tenant_id == item.tenant_id,
                OrganizationUnitClosure.ancestor_id == item.id,
                OrganizationUnitClosure.depth > 0,
            )
            .all()
        ]
        if not descendant_ids:
            return []
        return (
            self.db.query(OrganizationUnit)
            .filter(OrganizationUnit.tenant_id == item.tenant_id, OrganizationUnit.id.in_(descendant_ids))
            .order_by(OrganizationUnit.display_order.asc(), OrganizationUnit.unit_name.asc())
            .all()
        )

    def ancestors(self, item: OrganizationUnit) -> List[OrganizationUnit]:
        ancestor_ids = [
            row.ancestor_id
            for row in self.db.query(OrganizationUnitClosure)
            .filter(
                OrganizationUnitClosure.tenant_id == item.tenant_id,
                OrganizationUnitClosure.descendant_id == item.id,
                OrganizationUnitClosure.depth > 0,
            )
            .all()
        ]
        if not ancestor_ids:
            return []
        return (
            self.db.query(OrganizationUnit)
            .filter(OrganizationUnit.tenant_id == item.tenant_id, OrganizationUnit.id.in_(ancestor_ids))
            .order_by(OrganizationUnit.display_order.asc(), OrganizationUnit.unit_name.asc())
            .all()
        )

    def record_audit(
        self,
        action: str,
        item: OrganizationUnit,
        changed_by: Optional[str] = None,
        data: Optional[dict] = None,
    ) -> None:
        payload = data if data is not None else self._serialize(item)
        audit = OrganizationUnitAudit(
            id=str(uuid4()),
            tenant_id=item.tenant_id,
            organization_unit_id=item.id,
            action=action,
            changed_by=changed_by,
            data=payload,
        )
        self.db.add(audit)
        self.db.commit()

    def rebuild_closure_entries(self, item: OrganizationUnit) -> None:
        subtree_rows = (
            self.db.query(OrganizationUnitClosure.descendant_id, OrganizationUnitClosure.depth)
            .filter(
                OrganizationUnitClosure.tenant_id == item.tenant_id,
                OrganizationUnitClosure.ancestor_id == item.id,
            )
            .order_by(OrganizationUnitClosure.depth.asc())
            .all()
        )
        subtree_ids = [item.id] + [row.descendant_id for row in subtree_rows if row.depth > 0]

        self.db.query(OrganizationUnitClosure).filter(
            OrganizationUnitClosure.tenant_id == item.tenant_id,
            OrganizationUnitClosure.descendant_id.in_(subtree_ids),
        ).delete(synchronize_session=False)
        self.db.commit()

        units = (
            self.db.query(OrganizationUnit)
            .filter(OrganizationUnit.tenant_id == item.tenant_id, OrganizationUnit.id.in_(subtree_ids))
            .all()
        )
        units_by_id = {unit.id: unit for unit in units}
        ordered_units = [units_by_id[item.id]] + [units_by_id[row.descendant_id] for row in subtree_rows if row.depth > 0]

        for unit in ordered_units:
            self.create_closure_entries(unit)

    def _serialize(self, item: OrganizationUnit) -> dict:
        return {column.name: getattr(item, column.name) for column in item.__table__.columns}

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
