"""
GST API Router
FastAPI endpoints for GST operations
"""

from datetime import date
from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user
from backend.services.accounting.gst_service import GSTService
from backend.shared.database.accounting_extended_models import (
    GSTTransactionType,
    GSTReturnType
)


router = APIRouter(prefix="/accounting/gst", tags=["GST"])


def get_gst_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> GSTService:
    """Dependency to get GST service"""
    return GSTService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"]
    )


# ============================================================================
# GST Configuration Endpoints
# ============================================================================

@router.post("/configuration", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_gst_configuration(
    config_data: dict,
    service: GSTService = Depends(get_gst_service)
):
    """Create GST configuration"""
    try:
        config = await service.create_gst_configuration(
            gstin=config_data["gstin"],
            legal_name=config_data["legal_name"],
            state_code=config_data["state_code"],
            state_name=config_data["state_name"],
            address=config_data["address"],
            pincode=config_data["pincode"],
            registration_date=config_data["registration_date"],
            registration_type=config_data.get("registration_type", "regular"),
            trade_name=config_data.get("trade_name"),
            email=config_data.get("email"),
            phone=config_data.get("phone")
        )
        
        return success_response(
            data={
                "id": config.id,
                "gstin": config.gstin,
                "legal_name": config.legal_name,
                "state_name": config.state_name,
                "registration_type": config.registration_type
            },
            message="GST configuration created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configuration/{gstin}", response_model=dict)
async def get_gst_configuration(
    gstin: str,
    service: GSTService = Depends(get_gst_service)
):
    """Get GST configuration"""
    try:
        config = await service.get_gst_configuration(gstin)
        if not config:
            raise HTTPException(status_code=404, detail="GST configuration not found")
        
        return success_response(
            data={
                "id": config.id,
                "gstin": config.gstin,
                "legal_name": config.legal_name,
                "trade_name": config.trade_name,
                "state_code": config.state_code,
                "state_name": config.state_name,
                "address": config.address,
                "pincode": config.pincode,
                "registration_date": str(config.registration_date),
                "registration_type": config.registration_type,
                "email": config.email,
                "phone": config.phone,
                "is_active": config.is_active
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HSN/SAC Master Endpoints
# ============================================================================

@router.post("/hsn-sac", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_hsn_sac(
    hsn_data: dict,
    service: GSTService = Depends(get_gst_service)
):
    """Create HSN/SAC code"""
    try:
        hsn_sac = await service.create_hsn_sac(
            code=hsn_data["code"],
            code_type=hsn_data["code_type"],
            description=hsn_data["description"],
            cgst_rate=Decimal(str(hsn_data["cgst_rate"])),
            sgst_rate=Decimal(str(hsn_data["sgst_rate"])),
            igst_rate=Decimal(str(hsn_data["igst_rate"])),
            cess_rate=Decimal(str(hsn_data.get("cess_rate", 0))),
            category=hsn_data.get("category")
        )
        
        return success_response(
            data={
                "id": hsn_sac.id,
                "code": hsn_sac.code,
                "code_type": hsn_sac.code_type,
                "description": hsn_sac.description,
                "cgst_rate": float(hsn_sac.cgst_rate),
                "sgst_rate": float(hsn_sac.sgst_rate),
                "igst_rate": float(hsn_sac.igst_rate),
                "cess_rate": float(hsn_sac.cess_rate)
            },
            message="HSN/SAC code created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hsn-sac/{code}", response_model=dict)
async def get_hsn_sac(
    code: str,
    service: GSTService = Depends(get_gst_service)
):
    """Get HSN/SAC by code"""
    try:
        hsn_sac = await service.get_hsn_sac(code)
        if not hsn_sac:
            raise HTTPException(status_code=404, detail="HSN/SAC code not found")
        
        return success_response(
            data={
                "id": hsn_sac.id,
                "code": hsn_sac.code,
                "code_type": hsn_sac.code_type,
                "description": hsn_sac.description,
                "cgst_rate": float(hsn_sac.cgst_rate),
                "sgst_rate": float(hsn_sac.sgst_rate),
                "igst_rate": float(hsn_sac.igst_rate),
                "cess_rate": float(hsn_sac.cess_rate),
                "category": hsn_sac.category
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GST Calculation Endpoints
# ============================================================================

@router.post("/calculate", response_model=dict)
async def calculate_gst(
    calc_data: dict,
    service: GSTService = Depends(get_gst_service)
):
    """Calculate GST amounts"""
    try:
        result = await service.calculate_gst(
            taxable_amount=Decimal(str(calc_data["taxable_amount"])),
            hsn_sac_code=calc_data["hsn_sac_code"],
            is_inter_state=calc_data["is_inter_state"],
            is_reverse_charge=calc_data.get("is_reverse_charge", False)
        )
        
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GST Transaction Endpoints
# ============================================================================

@router.post("/transactions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def record_gst_transaction(
    txn_data: dict,
    service: GSTService = Depends(get_gst_service)
):
    """Record GST transaction"""
    try:
        transaction = await service.record_gst_transaction(
            transaction_date=txn_data["transaction_date"],
            transaction_type=GSTTransactionType(txn_data["transaction_type"]),
            reference_type=txn_data["reference_type"],
            reference_id=txn_data["reference_id"],
            party_name=txn_data["party_name"],
            taxable_amount=Decimal(str(txn_data["taxable_amount"])),
            cgst_amount=Decimal(str(txn_data.get("cgst_amount", 0))),
            sgst_amount=Decimal(str(txn_data.get("sgst_amount", 0))),
            igst_amount=Decimal(str(txn_data.get("igst_amount", 0))),
            cess_amount=Decimal(str(txn_data.get("cess_amount", 0))),
            party_gstin=txn_data.get("party_gstin"),
            party_state=txn_data.get("party_state"),
            hsn_sac_code=txn_data.get("hsn_sac_code"),
            invoice_number=txn_data.get("invoice_number"),
            place_of_supply=txn_data.get("place_of_supply"),
            is_reverse_charge=txn_data.get("is_reverse_charge", False)
        )
        
        return success_response(
            data={
                "id": transaction.id,
                "transaction_number": transaction.transaction_number,
                "transaction_date": str(transaction.transaction_date),
                "transaction_type": transaction.transaction_type,
                "party_name": transaction.party_name,
                "taxable_amount": float(transaction.taxable_amount),
                "total_gst": float(transaction.total_gst),
                "total_amount": float(transaction.total_amount)
            },
            message="GST transaction recorded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Input Tax Credit Endpoints
# ============================================================================

@router.post("/input-credit", response_model=dict, status_code=status.HTTP_201_CREATED)
async def record_input_credit(
    itc_data: dict,
    service: GSTService = Depends(get_gst_service)
):
    """Record input tax credit"""
    try:
        itc = await service.record_input_credit(
            supplier_gstin=itc_data["supplier_gstin"],
            supplier_name=itc_data["supplier_name"],
            invoice_number=itc_data["invoice_number"],
            invoice_date=itc_data["invoice_date"],
            taxable_amount=Decimal(str(itc_data["taxable_amount"])),
            cgst_amount=Decimal(str(itc_data.get("cgst_amount", 0))),
            sgst_amount=Decimal(str(itc_data.get("sgst_amount", 0))),
            igst_amount=Decimal(str(itc_data.get("igst_amount", 0))),
            cess_amount=Decimal(str(itc_data.get("cess_amount", 0))),
            transaction_id=itc_data.get("transaction_id")
        )
        
        return success_response(
            data={
                "id": itc.id,
                "supplier_name": itc.supplier_name,
                "invoice_number": itc.invoice_number,
                "invoice_date": str(itc.invoice_date),
                "taxable_amount": float(itc.taxable_amount),
                "total_itc": float(itc.total_itc),
                "itc_available": float(itc.itc_available)
            },
            message="Input tax credit recorded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GST Returns Endpoints
# ============================================================================

@router.post("/returns/gstr1", response_model=dict, status_code=status.HTTP_201_CREATED)
async def prepare_gstr1(
    return_data: dict,
    service: GSTService = Depends(get_gst_service)
):
    """Prepare GSTR-1 (Outward supplies)"""
    try:
        gst_return = await service.prepare_gstr1(
            gstin=return_data["gstin"],
            financial_year=return_data["financial_year"],
            month=return_data["month"]
        )
        
        return success_response(
            data={
                "id": gst_return.id,
                "return_type": gst_return.return_type,
                "return_period": gst_return.return_period,
                "due_date": str(gst_return.due_date),
                "outward_taxable": float(gst_return.outward_taxable),
                "outward_cgst": float(gst_return.outward_cgst),
                "outward_sgst": float(gst_return.outward_sgst),
                "outward_igst": float(gst_return.outward_igst),
                "status": gst_return.status
            },
            message="GSTR-1 prepared successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/returns/gstr3b", response_model=dict, status_code=status.HTTP_201_CREATED)
async def prepare_gstr3b(
    return_data: dict,
    service: GSTService = Depends(get_gst_service)
):
    """Prepare GSTR-3B (Summary return)"""
    try:
        gst_return = await service.prepare_gstr3b(
            gstin=return_data["gstin"],
            financial_year=return_data["financial_year"],
            month=return_data["month"]
        )
        
        return success_response(
            data={
                "id": gst_return.id,
                "return_type": gst_return.return_type,
                "return_period": gst_return.return_period,
                "due_date": str(gst_return.due_date),
                "outward_taxable": float(gst_return.outward_taxable),
                "outward_cgst": float(gst_return.outward_cgst),
                "outward_sgst": float(gst_return.outward_sgst),
                "outward_igst": float(gst_return.outward_igst),
                "itc_cgst": float(gst_return.itc_cgst),
                "itc_sgst": float(gst_return.itc_sgst),
                "itc_igst": float(gst_return.itc_igst),
                "net_cgst": float(gst_return.net_cgst),
                "net_sgst": float(gst_return.net_sgst),
                "net_igst": float(gst_return.net_igst),
                "total_liability": float(gst_return.total_liability),
                "status": gst_return.status
            },
            message="GSTR-3B prepared successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GST Reports Endpoints
# ============================================================================

@router.get("/reports/summary", response_model=dict)
async def get_gst_summary(
    financial_year: int = Query(...),
    month: Optional[int] = None,
    service: GSTService = Depends(get_gst_service)
):
    """Get GST summary"""
    try:
        summary = await service.get_gst_summary(
            financial_year=financial_year,
            month=month
        )
        
        return success_response(data=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
