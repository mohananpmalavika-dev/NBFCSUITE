from pydantic import BaseModel, Field
from typing import Optional

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
