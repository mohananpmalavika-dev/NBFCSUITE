from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class LegalEntityCreate(BaseModel):
    code: str
    name: str
    display_name: Optional[str] = None
    legal_type: Optional[str] = None
    country: Optional[str] = None
    incorporation_date: Optional[date] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    gst: Optional[str] = None
    description: Optional[str] = None


class LegalEntityResponse(BaseModel):
    id: str
    code: str
    name: str
    display_name: Optional[str]
    legal_type: Optional[str]
    status: str
    country: Optional[str]
    incorporation_date: Optional[date]
    cin: Optional[str]
    pan: Optional[str]
    gst: Optional[str]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class LegalEntityUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    legal_type: Optional[str] = None
    status: Optional[str] = None
    country: Optional[str] = None
    incorporation_date: Optional[date] = None
    cin: Optional[str] = None
    pan: Optional[str] = None
    gst: Optional[str] = None
    description: Optional[str] = None


class LegalEntityListResponse(BaseModel):
    total: int
    items: list[LegalEntityResponse]
