import uuid
from sqlalchemy import Column, String, DateTime, func, Text
from .db import Base

class Enterprise(Base):
    __tablename__ = 'enterprise'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    display_name = Column(String(256), nullable=True)
    short_name = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default='draft')
    currency_code = Column(String(8), nullable=True)
    timezone = Column(String(64), nullable=True)
    language = Column(String(16), nullable=True)
    fiscal_year_start = Column(String(10), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
