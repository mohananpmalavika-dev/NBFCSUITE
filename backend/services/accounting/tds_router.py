"""
TDS API Router
FastAPI endpoints for TDS operations
"""

from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.services.auth.dependencies import get_current_user
from backend.services.accounting.tds_service import TDSService
from backend.shared.database.accounting_extended_models import (
    TDSSection,
    TDSPaymentStatus,
    TDSReturnType
)


router = APIRouter(prefix="/accounting/tds", tags=["TDS"])


def get_tds_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> TDSService:
    """Dependency to get TDS service"""
    return TDSService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"]
    )


# ============================================================================
# TDS Section Master Endpoints
# ============================================================================

@router.post("/sections", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tds_section(
    section_data: dict,
    service: TDSService = Depends(get_tds_service)
):
    """Create or update TDS section configuration"""
    try:
        section = await service.create_tds_section(
            section_code=TDSSection(section_data["section_code"]),
            section_name=section_data["section_name"],
            financial_year=section_data["financial_year"],
            tds_rate=section_data["tds_rate"],
            threshold_limit=section_data.get("threshold_limit"),
            rate_without_pan=section_data.get("rate_without_pan"),
            description=section_data.get("description")
        )
        
        return success_response(
            data={
                "id": section.id,
                "section_code": section.section_code,
                "section_name": section.section_name,
                "financial_year": section.financial_year,
                "tds_rate": float(section.tds_rate),
                "threshold_limit": float(section.threshold_limit) if section.threshold_limit else None,
                "rate_without_pan": float(section.rate_without_pan) if section.rate_without_pan else None
            },
            message="TDS section configured successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sections", response_model=dict)
async def list_tds_sections(
    financial_year: int = Query(..., description="Financial year"),
    is_active: bool = True,
    service: TDSService = Depends(get_tds_service)
):
    """List all TDS sections for a financial year"""
    try:
        sections = await service.list_tds_sections(financial_year, is_active)
        
        return success_response(
            data={
                "sections": [
                    {
                        "id": s.id,
                        "section_code": s.section_code,
                        "section_name": s.section_name,
                        "financial_year": s.financial_year,
                        "tds_rate": float(s.tds_rate),
                        "threshold_limit": float(s.threshold_limit) if s.threshold_limit else None,
                        "rate_without_pan": float(s.rate_without_pan) if s.rate_without_pan else None,
                        "is_active": s.is_active
                    }
                    for s in sections
                ],
                "count": len(sections)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TDS Calculation Endpoints
# ============================================================================

@router.post("/calculate", response_model=dict)
async def calculate_tds(
    calculation_data: dict,
    service: TDSService = Depends(get_tds_service)
):
    """Calculate TDS amount"""
    try:
        result = await service.calculate_tds(
            section_code=TDSSection(calculation_data["section_code"]),
            gross_amount=calculation_data["gross_amount"],
            financial_year=calculation_data["financial_year"],
            has_pan=calculation_data.get("has_pan", True)
        )
        
        return success_response(data=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TDS Deduction Endpoints
# ============================================================================

@router.post("/deductions", response_model=dict, status_code=status.HTTP_201_CREATED)
async def record_tds_deduction(
    deduction_data: dict,
    service: TDSService = Depends(get_tds_service)
):
    """Record TDS deduction"""
    try:
        deduction = await service.record_tds_deduction(
            section_code=TDSSection(deduction_data["section_code"]),
            deduction_date=deduction_data["deduction_date"],
            deductee_type=deduction_data["deductee_type"],
            deductee_id=deduction_data["deductee_id"],
            deductee_name=deduction_data["deductee_name"],
            deductee_pan=deduction_data.get("deductee_pan"),
            transaction_type=deduction_data["transaction_type"],
            transaction_id=deduction_data["transaction_id"],
            gross_amount=deduction_data["gross_amount"],
            invoice_number=deduction_data.get("invoice_number")
        )
        
        if not deduction:
            return success_response(
                data={"below_threshold": True},
                message="Amount below TDS threshold, no deduction recorded"
            )
        
        return success_response(
            data={
                "id": deduction.id,
                "deduction_number": deduction.deduction_number,
                "deduction_date": str(deduction.deduction_date),
                "gross_amount": float(deduction.gross_amount),
                "tds_amount": float(deduction.tds_amount),
                "total_tds": float(deduction.total_tds),
                "net_amount": float(deduction.net_amount),
                "payment_status": deduction.payment_status
            },
            message="TDS deduction recorded successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/deductions", response_model=dict)
async def list_tds_deductions(
    financial_year: Optional[int] = None,
    quarter: Optional[int] = None,
    section_code: Optional[str] = None,
    payment_status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    service: TDSService = Depends(get_tds_service)
):
    """List TDS deductions with filters"""
    try:
        skip = (page - 1) * page_size
        
        section_enum = TDSSection(section_code) if section_code else None
        status_enum = TDSPaymentStatus(payment_status) if payment_status else None
        
        deductions, total = await service.list_tds_deductions(
            financial_year=financial_year,
            quarter=quarter,
            section_code=section_enum,
            payment_status=status_enum,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=page_size
        )
        
        return success_response(
            data={
                "deductions": [
                    {
                        "id": d.id,
                        "deduction_number": d.deduction_number,
                        "deduction_date": str(d.deduction_date),
                        "section_code": d.section_code,
                        "deductee_name": d.deductee_name,
                        "deductee_pan": d.deductee_pan,
                        "gross_amount": float(d.gross_amount),
                        "tds_amount": float(d.tds_amount),
                        "total_tds": float(d.total_tds),
                        "net_amount": float(d.net_amount),
                        "payment_status": d.payment_status,
                        "challan_id": d.challan_id,
                        "certificate_id": d.certificate_id
                    }
                    for d in deductions
                ],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TDS Challan Endpoints
# ============================================================================

@router.post("/challans", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tds_challan(
    challan_data: dict,
    service: TDSService = Depends(get_tds_service)
):
    """Create TDS payment challan"""
    try:
        challan = await service.create_tds_challan(
            financial_year=challan_data["financial_year"],
            quarter=challan_data["quarter"],
            section_code=TDSSection(challan_data["section_code"]),
            payment_date=challan_data["payment_date"],
            bsr_code=challan_data["bsr_code"],
            bank_name=challan_data["bank_name"],
            total_tds_amount=challan_data["total_tds_amount"],
            payment_mode=challan_data.get("payment_mode", "online"),
            cheque_number=challan_data.get("cheque_number"),
            transaction_reference=challan_data.get("transaction_reference"),
            deduction_ids=challan_data.get("deduction_ids")
        )
        
        return success_response(
            data={
                "id": challan.id,
                "challan_number": challan.challan_number,
                "payment_date": str(challan.payment_date),
                "total_amount": float(challan.total_amount),
                "bsr_code": challan.bsr_code,
                "bank_name": challan.bank_name,
                "payment_status": challan.payment_status
            },
            message="TDS challan created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/challans/pending-deductions", response_model=dict)
async def get_pending_deductions_for_challan(
    financial_year: int = Query(...),
    quarter: int = Query(...),
    section_code: Optional[str] = None,
    service: TDSService = Depends(get_tds_service)
):
    """Get pending TDS deductions for challan payment"""
    try:
        section_enum = TDSSection(section_code) if section_code else None
        deductions = await service.get_pending_deductions_for_challan(
            financial_year=financial_year,
            quarter=quarter,
            section_code=section_enum
        )
        
        total_tds = sum(d.total_tds for d in deductions)
        
        return success_response(
            data={
                "deductions": [
                    {
                        "id": d.id,
                        "deduction_number": d.deduction_number,
                        "deduction_date": str(d.deduction_date),
                        "deductee_name": d.deductee_name,
                        "gross_amount": float(d.gross_amount),
                        "total_tds": float(d.total_tds)
                    }
                    for d in deductions
                ],
                "count": len(deductions),
                "total_tds_amount": float(total_tds)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TDS Certificate Endpoints
# ============================================================================

@router.post("/certificates/generate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def generate_tds_certificate(
    certificate_data: dict,
    service: TDSService = Depends(get_tds_service)
):
    """Generate TDS Certificate (Form 16A)"""
    try:
        certificate = await service.generate_tds_certificate(
            financial_year=certificate_data["financial_year"],
            quarter=certificate_data["quarter"],
            deductee_id=certificate_data["deductee_id"],
            deductee_type=certificate_data["deductee_type"],
            deductee_name=certificate_data["deductee_name"],
            deductee_pan=certificate_data["deductee_pan"],
            deductee_address=certificate_data.get("deductee_address"),
            deductor_tan=certificate_data["deductor_tan"],
            deductor_pan=certificate_data["deductor_pan"],
            deductor_name=certificate_data["deductor_name"]
        )
        
        return success_response(
            data={
                "id": certificate.id,
                "certificate_number": certificate.certificate_number,
                "issue_date": str(certificate.issue_date),
                "financial_year": certificate.financial_year,
                "quarter": certificate.quarter,
                "deductee_name": certificate.deductee_name,
                "deductee_pan": certificate.deductee_pan,
                "total_gross_amount": float(certificate.total_gross_amount),
                "total_tds_amount": float(certificate.total_tds_amount),
                "status": certificate.status
            },
            message="TDS certificate generated successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TDS Return Endpoints
# ============================================================================

@router.post("/returns/prepare", response_model=dict, status_code=status.HTTP_201_CREATED)
async def prepare_tds_return(
    return_data: dict,
    service: TDSService = Depends(get_tds_service)
):
    """Prepare TDS return for filing (Form 26Q)"""
    try:
        return_type = TDSReturnType(return_data.get("return_type", "26Q"))
        tds_return = await service.prepare_tds_return(
            financial_year=return_data["financial_year"],
            quarter=return_data["quarter"],
            return_type=return_type
        )
        
        return success_response(
            data={
                "id": tds_return.id,
                "return_number": tds_return.return_number,
                "return_type": tds_return.return_type,
                "financial_year": tds_return.financial_year,
                "quarter": tds_return.quarter,
                "from_date": str(tds_return.from_date),
                "to_date": str(tds_return.to_date),
                "due_date": str(tds_return.due_date),
                "total_deductions": tds_return.total_deductions,
                "total_gross_amount": float(tds_return.total_gross_amount),
                "total_tds_amount": float(tds_return.total_tds_amount),
                "status": tds_return.status
            },
            message="TDS return prepared successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TDS Reports Endpoints
# ============================================================================

@router.get("/reports/summary", response_model=dict)
async def get_tds_summary(
    financial_year: int = Query(...),
    quarter: Optional[int] = None,
    service: TDSService = Depends(get_tds_service)
):
    """Get TDS summary for a period"""
    try:
        summary = await service.get_tds_summary(
            financial_year=financial_year,
            quarter=quarter
        )
        
        return success_response(data=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
