from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OrganizationUnitCreate(BaseModel):
    tenant_id: str = "default"
    parent_id: Optional[str] = None
    unit_code: str
    unit_name: str
    unit_type: str
    display_order: int = Field(default=0, ge=0)
    status: str = "active"
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    manager_position_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None
    address_id: Optional[str] = None


class OrganizationUnitUpdate(BaseModel):
    parent_id: Optional[str] = None
    unit_code: Optional[str] = None
    unit_name: Optional[str] = None
    unit_type: Optional[str] = None
    display_order: Optional[int] = Field(default=None, ge=0)
    status: Optional[str] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    manager_position_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    profit_center_id: Optional[str] = None
    address_id: Optional[str] = None


class OrganizationUnitResponse(OrganizationUnitCreate):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrganizationUnitTreeResponse(OrganizationUnitResponse):
    children: List["OrganizationUnitTreeResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True


class OrganizationAnalyticsResponse(BaseModel):
    total_units: int
    active_units: int
    inactive_units: int
    by_type: dict
