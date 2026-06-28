from datetime import datetime

from sqlalchemy import Column, DateTime, JSON, String

from app.database import Base


class OrganizationUnitAudit(Base):
    __tablename__ = "organization_unit_audit"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    organization_unit_id = Column(String, index=True, nullable=False)
    action = Column(String, nullable=False)
    changed_by = Column(String, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON, nullable=True)
