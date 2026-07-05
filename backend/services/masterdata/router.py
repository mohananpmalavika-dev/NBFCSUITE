"""
Master Data Router
API endpoints for master data management
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import math

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.shared.database.master_data_models import (
    Country, State, City, Pincode,
    Bank, BankBranch,
    Currency, DocumentType, Occupation, Industry
)
from backend.services.masterdata.service import MasterDataService
from backend.services.masterdata.schemas import *
from backend.services.auth.dependencies import get_current_active_user


router = APIRouter()


def get_master_service(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_active_user)
) -> MasterDataService:
    """Get master data service instance"""
    return MasterDataService(db, current_user.tenant_id)


# ============================================
# STATISTICS & OVERVIEW
# ============================================

@router.get(
    "/stats",
    summary="Get master data statistics",
    description="Get counts of all master data types"
)
async def get_stats(
    service: MasterDataService = Depends(get_master_service)
):
    """Get master data statistics"""
    stats = await service.get_stats()
    return success_response(data=stats)


# ============================================
# COUNTRIES
# ============================================

@router.get(
    "/countries",
    response_model=dict,
    summary="List countries",
    description="Get paginated list of countries"
)
async def list_countries(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List countries with pagination"""
    records, total = await service.get_list(
        Country, page, page_size, search, is_active
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [CountryResponse.from_orm(r).dict() for r in records]
    })


@router.post(
    "/countries",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create country"
)
async def create_country(
    data: CountryCreate,
    service: MasterDataService = Depends(get_master_service)
):
    """Create new country"""
    record = await service.create(Country, data.dict())
    return success_response(
        data=CountryResponse.from_orm(record).dict(),
        status_code=status.HTTP_201_CREATED
    )


# ============================================
# STATES
# ============================================

@router.get(
    "/states",
    response_model=dict,
    summary="List states"
)
async def list_states(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List states with pagination"""
    records, total = await service.get_list(
        State, page, page_size, search, is_active
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [StateResponse.from_orm(r).dict() for r in records]
    })


@router.post(
    "/states",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create state"
)
async def create_state(
    data: StateCreate,
    service: MasterDataService = Depends(get_master_service)
):
    """Create new state"""
    record = await service.create(State, data.dict())
    return success_response(
        data=StateResponse.from_orm(record).dict(),
        status_code=status.HTTP_201_CREATED
    )


# ============================================
# CITIES
# ============================================

@router.get(
    "/cities",
    response_model=dict,
    summary="List cities"
)
async def list_cities(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List cities with pagination"""
    records, total = await service.get_list(
        City, page, page_size, search, is_active
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [CityResponse.from_orm(r).dict() for r in records]
    })


# ============================================
# PINCODES
# ============================================

@router.get(
    "/pincodes",
    response_model=dict,
    summary="List pincodes"
)
async def list_pincodes(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List pincodes with pagination"""
    records, total = await service.get_list(
        Pincode, page, page_size, search
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [PincodeResponse.from_orm(r).dict() for r in records]
    })


@router.get(
    "/pincodes/search/{pincode}",
    response_model=dict,
    summary="Search pincode"
)
async def search_pincode(
    pincode: str,
    service: MasterDataService = Depends(get_master_service)
):
    """Search by pincode"""
    records = await service.search_pincode(pincode)
    return success_response(data={
        "pincode": pincode,
        "results": [PincodeResponse.from_orm(r).dict() for r in records]
    })


# ============================================
# BANKS
# ============================================

@router.get(
    "/banks",
    response_model=dict,
    summary="List banks"
)
async def list_banks(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List banks with pagination"""
    records, total = await service.get_list(
        Bank, page, page_size, search, is_active
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [BankResponse.from_orm(r).dict() for r in records]
    })


@router.post(
    "/banks",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create bank"
)
async def create_bank(
    data: BankCreate,
    service: MasterDataService = Depends(get_master_service)
):
    """Create new bank"""
    record = await service.create(Bank, data.dict())
    return success_response(
        data=BankResponse.from_orm(record).dict(),
        status_code=status.HTTP_201_CREATED
    )


# ============================================
# BANK BRANCHES
# ============================================

@router.get(
    "/bank-branches",
    response_model=dict,
    summary="List bank branches"
)
async def list_bank_branches(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List bank branches with pagination"""
    records, total = await service.get_list(
        BankBranch, page, page_size, search
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [BankBranchResponse.from_orm(r).dict() for r in records]
    })


@router.get(
    "/bank-branches/ifsc/{ifsc_code}",
    response_model=dict,
    summary="Search by IFSC code"
)
async def search_ifsc(
    ifsc_code: str,
    service: MasterDataService = Depends(get_master_service)
):
    """Search bank branch by IFSC code"""
    record = await service.search_ifsc(ifsc_code)
    
    if not record:
        return success_response(data=None, message="IFSC code not found")
    
    return success_response(data=BankBranchResponse.from_orm(record).dict())


# ============================================
# DOCUMENT TYPES
# ============================================

@router.get(
    "/document-types",
    response_model=dict,
    summary="List document types"
)
async def list_document_types(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List document types with pagination"""
    records, total = await service.get_list(
        DocumentType, page, page_size, search, is_active
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [DocumentTypeResponse.from_orm(r).dict() for r in records]
    })


@router.post(
    "/document-types",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create document type"
)
async def create_document_type(
    data: DocumentTypeCreate,
    service: MasterDataService = Depends(get_master_service)
):
    """Create new document type"""
    record = await service.create(DocumentType, data.dict())
    return success_response(
        data=DocumentTypeResponse.from_orm(record).dict(),
        status_code=status.HTTP_201_CREATED
    )


# ============================================
# OCCUPATIONS
# ============================================

@router.get(
    "/occupations",
    response_model=dict,
    summary="List occupations"
)
async def list_occupations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List occupations with pagination"""
    records, total = await service.get_list(
        Occupation, page, page_size, search, is_active
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [OccupationResponse.from_orm(r).dict() for r in records]
    })


@router.post(
    "/occupations",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create occupation"
)
async def create_occupation(
    data: OccupationCreate,
    service: MasterDataService = Depends(get_master_service)
):
    """Create new occupation"""
    record = await service.create(Occupation, data.dict())
    return success_response(
        data=OccupationResponse.from_orm(record).dict(),
        status_code=status.HTTP_201_CREATED
    )


# ============================================
# INDUSTRIES
# ============================================

@router.get(
    "/industries",
    response_model=dict,
    summary="List industries"
)
async def list_industries(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    service: MasterDataService = Depends(get_master_service)
):
    """List industries with pagination"""
    records, total = await service.get_list(
        Industry, page, page_size, search, is_active
    )
    
    return success_response(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size),
        "items": [r.dict() for r in records]
    })
