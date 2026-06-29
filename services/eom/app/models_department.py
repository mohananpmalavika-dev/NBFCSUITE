import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class Department(Base):
    __tablename__ = 'department'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default='active')
    department_head = Column(String(128), nullable=True)
    branch_id = Column(String(36), ForeignKey('branch.id'), nullable=True)
    business_unit_id = Column(String(36), ForeignKey('business_unit.id'), nullable=True)
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=True)
    city = Column(String(128), nullable=True)
    region = Column(String(128), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    branch = relationship('Branch', backref='departments')
    business_unit = relationship('BusinessUnit')
    legal_entity = relationship('LegalEntity')
