from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Table, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

# Association table for User-Role many-to-many
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id')),
    Column('role_id', String, ForeignKey('roles.id'))
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, nullable=True, index=True)
    organization_id = Column(String, nullable=True, index=True)
    zone_id = Column(String, nullable=True, index=True)
    region_id = Column(String, nullable=True, index=True)
    area_id = Column(String, nullable=True, index=True)
    branch_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    users = relationship("User", secondary=user_roles, back_populates="roles")


class TenantConfiguration(Base):
    __tablename__ = "tenant_configurations"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    tenant_id = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    legal_name = Column(String, nullable=True)
    primary_color = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
