from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, Field


class BaseEOMCreate(BaseModel):
    tenant_id: str


class BrandCreate(BaseEOMCreate):
    brand_code: str
    brand_name: str
    legal_name: Optional[str] = None
    short_name: Optional[str] = None
    logo_url: Optional[str] = None
    theme_color: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gst: Optional[str] = None
    pan: Optional[str] = None
    cin: Optional[str] = None
    license_no: Optional[str] = None
    registration_no: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    currency: Optional[str] = "INR"


class LegalEntityCreate(BaseEOMCreate):
    brand_id: str
    entity_code: str
    entity_name: str
    entity_type: Optional[str] = "company"
    gst: Optional[str] = None
    pan: Optional[str] = None
    tan: Optional[str] = None
    cin: Optional[str] = None
    registered_address: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    license: Optional[str] = None


class BusinessUnitCreate(BaseEOMCreate):
    legal_entity_id: str
    business_unit_code: str
    business_unit_name: str
    head: Optional[str] = None


class ZoneCreate(BaseEOMCreate):
    business_unit_id: str
    zone_code: str
    zone_name: str
    zone_head: Optional[str] = None


class RegionCreate(BaseEOMCreate):
    zone_id: str
    region_code: str
    region_name: str
    regional_manager: Optional[str] = None
    office_address: Optional[str] = None


class AreaCreate(BaseEOMCreate):
    region_id: str
    area_code: str
    area_name: str
    area_manager: Optional[str] = None
    office_address: Optional[str] = None


class ClusterCreate(BaseEOMCreate):
    area_id: str
    cluster_code: str
    cluster_name: str
    cluster_manager: Optional[str] = None


class BranchCreate(BaseEOMCreate):
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: str
    cluster_id: Optional[str] = None

    branch_code: Optional[str] = None
    branch_name: str
    short_name: Optional[str] = None
    branch_type: Optional[str] = None
    branch_category: Optional[str] = None
    branch_types: Optional[Any] = None

    door_no: Optional[str] = None
    building: Optional[str] = None
    street: Optional[str] = None
    village: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = "India"
    pincode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    contact_phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    website: Optional[str] = None


class DepartmentCreate(BaseEOMCreate):
    branch_id: str
    department_code: str
    department_name: str


class EmployeeCreate(BaseEOMCreate):
    employee_name: str
    employee_code: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class EmployeeHierarchyCreate(BaseEOMCreate):
    employee_id: str

    brand_id: Optional[str] = None
    legal_entity_id: Optional[str] = None
    business_unit_id: Optional[str] = None
    zone_id: Optional[str] = None
    region_id: Optional[str] = None
    area_id: Optional[str] = None
    cluster_id: Optional[str] = None
    branch_id: Optional[str] = None
    department_id: Optional[str] = None

    position_title: Optional[str] = None


class CustomerBranchMappingCreate(BaseEOMCreate):
    customer_id: str
    branch_id: str
    transferred_by: Optional[str] = None


class BrandResponse(BrandCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LegalEntityResponse(LegalEntityCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessUnitResponse(BusinessUnitCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ZoneResponse(ZoneCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegionResponse(RegionCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AreaResponse(AreaCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClusterResponse(ClusterCreate):
    id: str
    status: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BranchResponse(BranchCreate):
    id: str
    branch_code: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DepartmentResponse(DepartmentCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeResponse(EmployeeCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeHierarchyResponse(EmployeeHierarchyCreate):
    id: str
    status: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerBranchMappingResponse(CustomerBranchMappingCreate):
    id: str
    status: str
    effective_from: datetime
    effective_to: Optional[datetime] = None
    transferred_from_branch_id: Optional[str] = None
    transferred_at: Optional[datetime] = None

    class Config:
        from_attributes = True

