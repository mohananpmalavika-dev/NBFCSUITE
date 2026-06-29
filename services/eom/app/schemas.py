from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .schemas_branch import BranchCreate, BranchResponse, BranchUpdate, BranchListResponse, BranchDashboardResponse, BranchHealthResponse, BranchAnalyticsResponse

class EnterpriseCreate(BaseModel):
    code: str = Field(..., min_length=2)
    name: str
    display_name: Optional[str] = None
    short_name: Optional[str] = None
    currency_code: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    fiscal_year_start: Optional[str] = None
    description: Optional[str] = None

class EnterpriseResponse(BaseModel):
    id: str
    code: str
    name: str
    display_name: Optional[str]
    short_name: Optional[str]
    status: str
    currency_code: Optional[str]
    timezone: Optional[str]
    language: Optional[str]
    fiscal_year_start: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True


class EnterpriseUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    short_name: Optional[str] = None
    status: Optional[str] = None
    currency_code: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    fiscal_year_start: Optional[str] = None
    description: Optional[str] = None


class EnterpriseListResponse(BaseModel):
    total: int
    items: list[EnterpriseResponse]


class BrandCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class BrandResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str]
    status: str

    class Config:
        orm_mode = True


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class BrandListResponse(BaseModel):
    total: int
    items: list[BrandResponse]


class AuditEntryResponse(BaseModel):
    id: str
    entity_type: str
    entity_id: Optional[str]
    action: str
    payload: Optional[str]
    created_at: Optional[datetime]


class AuditListResponse(BaseModel):
    total: int
    items: list[AuditEntryResponse]


class GeographyNodeBase(BaseModel):
    code: str
    name: str
    node_type: str
    parent_id: Optional[str] = None
    status: Optional[str] = 'active'
    manager: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    population: Optional[float] = None
    area_size: Optional[float] = None
    description: Optional[str] = None
    business_unit_id: Optional[str] = None
    legal_entity_id: Optional[str] = None


class GeographyNodeCreate(GeographyNodeBase):
    pass


class GeographyNodeUpdate(BaseModel):
    name: Optional[str] = None
    node_type: Optional[str] = None
    parent_id: Optional[str] = None
    status: Optional[str] = None
    manager: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    population: Optional[float] = None
    area_size: Optional[float] = None
    description: Optional[str] = None
    business_unit_id: Optional[str] = None
    legal_entity_id: Optional[str] = None


class GeographyNodeResponse(GeographyNodeBase):
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class GeographyNodeListResponse(BaseModel):
    total: int
    items: list[GeographyNodeResponse]


class GeographyTreeNode(BaseModel):
    id: str
    code: str
    name: str
    node_type: str
    status: str
    manager: Optional[str] = None
    parent_id: Optional[str] = None
    children: list['GeographyTreeNode'] = Field(default_factory=list)

    class Config:
        orm_mode = True


GeographyTreeNode.update_forward_refs()


class GeographyTreeResponse(BaseModel):
    items: list[GeographyTreeNode]
