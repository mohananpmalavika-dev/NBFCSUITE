import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class Position(Base):
    __tablename__ = 'position'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    enterprise_id = Column(String(36), nullable=True)
    business_unit_id = Column(String(36), nullable=True)
    department_id = Column(String(36), nullable=True)
    section_id = Column(String(36), nullable=True)
    team_id = Column(String(36), nullable=True)
    grade_id = Column(String(36), nullable=True)
    code = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(256), nullable=False)
    status = Column(String(32), nullable=False, default='open')
    reports_to_position_id = Column(String(36), ForeignKey('position.id'), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # grade_id is intentionally not linked via a FK in this codebase.
    # Using relationship() without a ForeignKey causes SQLAlchemy mapper configuration failures.
    grade = None  # type: ignore
    team = None  # type: ignore
    reports_to = relationship('Position', remote_side=[id])
