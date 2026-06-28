from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class OrganizationUnit(Base):
    __tablename__ = "organization_units"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False, default="default")
    parent_id = Column(String, ForeignKey("organization_units.id"), nullable=True, index=True)
    unit_code = Column(String, index=True, nullable=False)
    unit_name = Column(String, nullable=False)
    unit_type = Column(String, index=True, nullable=False)
    display_order = Column(Integer, default=0)
    status = Column(String, default="active", index=True)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)
    manager_position_id = Column(String, nullable=True)
    cost_center_id = Column(String, nullable=True)
    profit_center_id = Column(String, nullable=True)
    address_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
