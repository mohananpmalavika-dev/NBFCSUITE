from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship

from .db import Base


class Enterprise(Base):
    __tablename__ = "enterprises"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    enterprise_code = Column(String, nullable=False)
    enterprise_name = Column(String, nullable=False)
    logo_url = Column(String)
    vision = Column(String)
    mission = Column(String)
    corporate_address = Column(String)
    corporate_office = Column(String)
    country = Column(String, default="India")
    currency = Column(String, default="INR")
    timezone = Column(String, default="Asia/Kolkata")
    financial_year_start = Column(String, default="04-01")
    financial_year_end = Column(String, default="03-31")

    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Brand(Base):
    __tablename__ = "brands"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    enterprise_id = Column(String, ForeignKey("enterprises.id"), nullable=True)
    brand_code = Column(String, nullable=False)
    brand_name = Column(String, nullable=False)

    legal_name = Column(String)
    short_name = Column(String)
    logo_url = Column(String)
    theme_color = Column(String)
    website = Column(String)
    email = Column(String)
    phone = Column(String)
    gst = Column(String)
    pan = Column(String)
    cin = Column(String)
    license_no = Column(String)
    registration_no = Column(String)
    country = Column(String)
    state = Column(String)
    timezone = Column(String, default="Asia/Kolkata")
    currency = Column(String, default="INR")

    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    enterprise = relationship("Enterprise")


class LegalEntity(Base):
    __tablename__ = "legal_entities"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    brand_id = Column(String, ForeignKey("brands.id"), nullable=False)
    entity_code = Column(String, nullable=False)
    entity_name = Column(String, nullable=False)
    entity_type = Column(String, default="company")

    gst = Column(String)
    pan = Column(String)
    tan = Column(String)
    cin = Column(String)
    registered_address = Column(String)
    state = Column(String)
    country = Column(String)
    license = Column(String)

    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("Brand")


class BusinessUnit(Base):
    __tablename__ = "business_units"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    legal_entity_id = Column(String, ForeignKey("legal_entities.id"), nullable=False)
    business_unit_code = Column(String, nullable=False)
    business_unit_name = Column(String, nullable=False)
    head = Column(String)
    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    legal_entity = relationship("LegalEntity")


class Division(Base):
    __tablename__ = "divisions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    business_unit_id = Column(String, ForeignKey("business_units.id"), nullable=False)
    division_code = Column(String, nullable=False)
    division_name = Column(String, nullable=False)
    division_head = Column(String)
    status = Column(String, default="active")

    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    business_unit = relationship("BusinessUnit")


class EOMZone(Base):
    __tablename__ = "eom_zones"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    business_unit_id = Column(String, ForeignKey("business_units.id"), nullable=False)
    division_id = Column(String, ForeignKey("divisions.id"), nullable=True)
    zone_code = Column(String, nullable=False)
    zone_name = Column(String, nullable=False)
    zone_head = Column(String)
    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    business_unit = relationship("BusinessUnit")
    division = relationship("Division")


class EOMRegion(Base):
    __tablename__ = "eom_regions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    zone_id = Column(String, ForeignKey("eom_zones.id"), nullable=False)
    region_code = Column(String, nullable=False)
    region_name = Column(String, nullable=False)
    regional_manager = Column(String)
    office_address = Column(String)
    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    zone = relationship("EOMZone")


class EOMArea(Base):
    __tablename__ = "eom_areas"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    region_id = Column(String, ForeignKey("eom_regions.id"), nullable=False)
    area_code = Column(String, nullable=False)
    area_name = Column(String, nullable=False)
    area_manager = Column(String)
    office_address = Column(String)
    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    region = relationship("EOMRegion")


class EOMCluster(Base):
    __tablename__ = "eom_clusters"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    area_id = Column(String, ForeignKey("eom_areas.id"), nullable=False)
    cluster_code = Column(String, nullable=False)
    cluster_name = Column(String, nullable=False)
    cluster_manager = Column(String)
    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    area = relationship("EOMArea")


class EOMBranch(Base):
    __tablename__ = "eom_branches"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    branch_code = Column(String, nullable=False)

    zone_id = Column(String, ForeignKey("eom_zones.id"), nullable=True)
    region_id = Column(String, ForeignKey("eom_regions.id"), nullable=True)
    area_id = Column(String, ForeignKey("eom_areas.id"), nullable=False)
    cluster_id = Column(String, ForeignKey("eom_clusters.id"), nullable=True)

    branch_name = Column(String, nullable=False)
    short_name = Column(String)
    branch_type = Column(String)
    branch_category = Column(String)
    branch_types = Column(JSON, nullable=True)

    door_no = Column(String)
    building = Column(String)
    street = Column(String)
    village = Column(String)
    city = Column(String)
    district = Column(String)
    state = Column(String)
    country = Column(String, default="India")
    pincode = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)

    contact_phone = Column(String)
    mobile = Column(String)
    email = Column(String)
    whatsapp = Column(String)
    website = Column(String)

    status = Column(String, default="draft")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Department(Base):
    __tablename__ = "departments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    branch_id = Column(String, ForeignKey("eom_branches.id"), nullable=False)
    department_code = Column(String, nullable=False)
    department_name = Column(String, nullable=False)

    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    department_id = Column(String, ForeignKey("departments.id"), nullable=False)
    team_code = Column(String, nullable=False)
    team_name = Column(String, nullable=False)
    team_lead_employee_id = Column(String, ForeignKey("employees.id"), nullable=True)

    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    employee_code = Column(String)
    employee_name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)

    status = Column(String, default="active")

    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Position(Base):
    __tablename__ = "positions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    team_id = Column(String, ForeignKey("teams.id"), nullable=True)
    position_code = Column(String, nullable=False)
    position_title = Column(String, nullable=False)
    reports_to_position_id = Column(String, ForeignKey("positions.id"), nullable=True)
    grade = Column(String)
    employment_type = Column(String, default="full_time")

    status = Column(String, default="open")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department")
    team = relationship("Team", foreign_keys=[team_id])
    reports_to = relationship("Position", remote_side=[id])


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    vendor_code = Column(String, nullable=False)
    vendor_name = Column(String, nullable=False)
    vendor_type = Column(String)
    contact_person = Column(String)
    email = Column(String)
    phone = Column(String)
    gst = Column(String)
    pan = Column(String)

    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    asset_code = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_type = Column(String)
    branch_id = Column(String, ForeignKey("eom_branches.id"), nullable=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)
    assigned_employee_id = Column(String, ForeignKey("employees.id"), nullable=True)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=True)
    purchase_value = Column(Float, default=0)

    status = Column(String, default="active")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    branch = relationship("EOMBranch")
    department = relationship("Department")
    vendor = relationship("Vendor")


class EmployeeHierarchy(Base):
    __tablename__ = "employee_hierarchy"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    employee_id = Column(String, ForeignKey("employees.id"), nullable=False)

    brand_id = Column(String, ForeignKey("brands.id"), nullable=True)
    legal_entity_id = Column(String, ForeignKey("legal_entities.id"), nullable=True)
    business_unit_id = Column(String, ForeignKey("business_units.id"), nullable=True)
    division_id = Column(String, ForeignKey("divisions.id"), nullable=True)
    zone_id = Column(String, ForeignKey("eom_zones.id"), nullable=True)
    region_id = Column(String, ForeignKey("eom_regions.id"), nullable=True)
    area_id = Column(String, ForeignKey("eom_areas.id"), nullable=True)
    cluster_id = Column(String, ForeignKey("eom_clusters.id"), nullable=True)
    branch_id = Column(String, ForeignKey("eom_branches.id"), nullable=True)
    department_id = Column(String, ForeignKey("departments.id"), nullable=True)

    position_title = Column(String)
    status = Column(String, default="active")

    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class CustomerBranchMapping(Base):
    __tablename__ = "customer_branch_mapping"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)

    customer_id = Column(String, nullable=False)
    branch_id = Column(String, ForeignKey("eom_branches.id"), nullable=False)

    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime, nullable=True)
    status = Column(String, default="active")

    transferred_from_branch_id = Column(String, ForeignKey("eom_branches.id"), nullable=True)
    transferred_by = Column(String)
    transferred_at = Column(DateTime, nullable=True)

    # Relationships can be added later.

