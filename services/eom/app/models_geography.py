import uuid
from sqlalchemy import Column, String, DateTime, Float, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base


class GeographyNode(Base):
    __tablename__ = 'geography_node'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    node_type = Column(String(64), nullable=False)
    parent_id = Column(String(36), ForeignKey('geography_node.id'), nullable=True)
    status = Column(String(32), nullable=False, default='active')
    manager = Column(String(128), nullable=True)
    latitude = Column(String(32), nullable=True)
    longitude = Column(String(32), nullable=True)
    population = Column(Float, nullable=True)
    area_size = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    business_unit_id = Column(String(36), ForeignKey('business_unit.id'), nullable=True)
    legal_entity_id = Column(String(36), ForeignKey('legal_entity.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    parent = relationship('GeographyNode', remote_side=[id], backref='children')
    business_unit = relationship('BusinessUnit', backref='geography_nodes')
    legal_entity = relationship('LegalEntity', backref='geography_nodes')
