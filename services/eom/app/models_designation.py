import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class Designation(Base):
    __tablename__ = 'designation'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)
    job_family_id = Column(String(36), nullable=True)
    grade_id = Column(String(36), nullable=True)
    department_id = Column(String(36), nullable=True)
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    short_name = Column(String(100), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    reports_to_designation_id = Column(String(36), ForeignKey('designation.id'), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    reports_to = relationship('Designation', remote_side=[id])
