import uuid
from sqlalchemy import Column, String, Date, DateTime, Text, func
from .db import Base


class LegalEntity(Base):
    __tablename__ = 'legal_entity'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    display_name = Column(String(256), nullable=True)
    legal_type = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    country = Column(String(64), nullable=True)
    incorporation_date = Column(Date, nullable=True)
    cin = Column(String(64), nullable=True)
    pan = Column(String(32), nullable=True)
    gst = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
