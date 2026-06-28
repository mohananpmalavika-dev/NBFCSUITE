from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from app.database import Base


class OrganizationUnitClosure(Base):
    __tablename__ = "organization_unit_closure"
    __table_args__ = (
        UniqueConstraint("tenant_id", "ancestor_id", "descendant_id", name="uq_organization_unit_closure"),
    )

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    ancestor_id = Column(String, ForeignKey("organization_units.id"), nullable=False, index=True)
    descendant_id = Column(String, ForeignKey("organization_units.id"), nullable=False, index=True)
    depth = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
