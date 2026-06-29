import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class Section(Base):
    __tablename__ = 'section'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    section_type = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    department_id = Column(String(36), ForeignKey('department.id'), nullable=True)
    section_head = Column(String(128), nullable=True)
    deputy_head = Column(String(128), nullable=True)
    business_unit_id = Column(String(36), ForeignKey('business_unit.id'), nullable=True)
    branch_id = Column(String(36), ForeignKey('branch.id'), nullable=True)
    reporting_department_id = Column(String(36), ForeignKey('department.id'), nullable=True)
    working_calendar = Column(String(64), nullable=True)
    shift = Column(String(64), nullable=True)
    capacity = Column(String(32), nullable=True)
    business_hours = Column(String(64), nullable=True)
    sla_profile = Column(String(128), nullable=True)
    service_catalog = Column(Text, nullable=True)
    business_capabilities = Column(Text, nullable=True)
    workflows = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    department = relationship('Department', backref='sections', foreign_keys=[department_id])
    reporting_department = relationship('Department', foreign_keys=[reporting_department_id])


class SectionHead(Base):
    __tablename__ = 'section_head'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String(36), ForeignKey('section.id'), nullable=False)
    employee_id = Column(String(36), nullable=False)
    role = Column(String(64), nullable=False)
    start_date = Column(String(32), nullable=True)
    end_date = Column(String(32), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    section = relationship('Section', backref='heads')


class SectionDocument(Base):
    __tablename__ = 'section_document'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String(36), ForeignKey('section.id'), nullable=False)
    document_type = Column(String(64), nullable=False)
    name = Column(String(256), nullable=False)
    file_reference = Column(String(256), nullable=True)
    status = Column(String(32), nullable=False, default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    section = relationship('Section', backref='documents')


class SectionWorkflow(Base):
    __tablename__ = 'section_workflow'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String(36), ForeignKey('section.id'), nullable=False)
    workflow_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default='pending')
    initiated_by = Column(String(128), nullable=True)
    initiated_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    remarks = Column(Text, nullable=True)

    section = relationship('Section', backref='workflows')


class SectionAudit(Base):
    __tablename__ = 'section_audit'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    section_id = Column(String(36), ForeignKey('section.id'), nullable=False)
    action = Column(String(64), nullable=False)
    payload = Column(Text, nullable=True)
    performed_by = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    section = relationship('Section', backref='audit_trail')
