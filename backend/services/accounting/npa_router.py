"""
NPA Management API Router
FastAPI endpoints for NPA classification, provisioning, and reporting
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response, error_response
from backend.services.auth.dependencies import get_current_user
from backend.services.accounting.npa_service import NPAService, NPACategory
from backend.services.accounting import npa_schemas


router = APIRouter(prefix="/accounting/npa", tags=["NPA Management"])


def get_npa_service(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> NPAService:
    """Dependency to get NPA service"""
    return NPAService(
        db=db,
        tenant_id=current_user["tenant_id"],
        user_id=current_user["id"]
    )


# ============================================================================
# NPA Classification Endpoints
# ============================================================================

@router.post("/classify", response_model=dict)
async def classify_asset(
    classification_request: npa_schemas.NPAClassificationRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Classify an asset based on days past due
    Returns NPA category and classification details
    """
    try:
        npa_category = service.classify_asset(
            days_past_due=classification_request.days_past_due,
            is_restructured=classification_request.is_restructured,
            is_written_off=classification_request.is_written_off
        )
        
        # Determine if it's NPA or SMA
        is_npa = npa_category in [
            NPACategory.SUBSTANDARD,
            NPACategory.DOUBTFUL_1,
            NPACategory.DOUBTFUL_2,
            NPACategory.DOUBTFUL_3,
            NPACategory.LOSS
        ]
        
        is_sma = npa_category in [
            NPACategory.SPECIAL_MENTION_0,
            NPACategory.SPECIAL_MENTION_1,
            NPACategory.SPECIAL_MENTION_2
        ]
        
        return success_response(
            data={
                "npa_category": npa_category.value,
                "days_past_due": classification_request.days_past_due,
                "is_npa": is_npa,
                "is_sma": is_sma,
                "classification_date": date.today()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classify/loan/{loan_account_id}", response_model=dict)
async def get_loan_classification(
    loan_account_id: int,
    as_of_date: Optional[date] = Query(None),
    service: NPAService = Depends(get_npa_service)
):
    """
    Get classification for a specific loan account
    """
    try:
        if as_of_date is None:
            as_of_date = date.today()
        
        classification = await service.get_loan_classification(
            loan_account_id=loan_account_id,
            as_of_date=as_of_date
        )
        
        return success_response(data=classification)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# Provisioning Calculation Endpoints
# ============================================================================

@router.post("/provisioning/calculate", response_model=dict)
async def calculate_provisioning(
    provisioning_request: npa_schemas.ProvisioningCalculationRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Calculate required provisioning for a loan
    """
    try:
        provisioning = service.calculate_provisioning_amount(
            outstanding_principal=provisioning_request.outstanding_principal,
            npa_category=provisioning_request.npa_category,
            is_secured=provisioning_request.is_secured,
            security_coverage_ratio=provisioning_request.security_coverage_ratio,
            existing_provision=provisioning_request.existing_provision
        )
        
        provisioning["npa_category"] = provisioning_request.npa_category.value
        
        return success_response(data=provisioning)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/provisioning/create", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_provision(
    provision_request: npa_schemas.CreateProvisionRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Create provisioning accounting entry for a loan
    """
    try:
        journal_entry = await service.create_provisioning_entry(
            loan_account_id=provision_request.loan_account_id,
            provision_amount=provision_request.provision_amount,
            npa_category=provision_request.npa_category,
            as_of_date=provision_request.as_of_date,
            narration=provision_request.narration
        )
        
        return success_response(
            data={
                "journal_entry_id": journal_entry.id,
                "entry_number": journal_entry.entry_number,
                "provision_amount": float(provision_request.provision_amount),
                "status": journal_entry.status.value
            },
            message="Provisioning entry created successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/provisioning/reverse", response_model=dict)
async def reverse_provision(
    reversal_request: npa_schemas.ReverseProvisionRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Reverse provisioning entry (on upgrade or recovery)
    """
    try:
        journal_entry = await service.reverse_provisioning_entry(
            loan_account_id=reversal_request.loan_account_id,
            provision_amount=reversal_request.provision_amount,
            as_of_date=reversal_request.as_of_date,
            narration=reversal_request.narration
        )
        
        return success_response(
            data={
                "journal_entry_id": journal_entry.id,
                "entry_number": journal_entry.entry_number,
                "reversed_amount": float(reversal_request.provision_amount),
                "status": journal_entry.status.value
            },
            message="Provisioning reversed successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/write-off", response_model=dict, status_code=status.HTTP_201_CREATED)
async def write_off_loan(
    write_off_request: npa_schemas.WriteOffRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Write off a loan (typically for LOSS category)
    """
    try:
        journal_entry = await service.create_write_off_entry(
            loan_account_id=write_off_request.loan_account_id,
            write_off_amount=write_off_request.write_off_amount,
            provision_available=write_off_request.provision_available,
            as_of_date=write_off_request.as_of_date,
            narration=write_off_request.narration
        )
        
        return success_response(
            data={
                "journal_entry_id": journal_entry.id,
                "entry_number": journal_entry.entry_number,
                "write_off_amount": float(write_off_request.write_off_amount),
                "provision_used": float(write_off_request.provision_available),
                "status": journal_entry.status.value
            },
            message="Loan written off successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================================
# Asset Classification Register Endpoints
# ============================================================================

@router.post("/register", response_model=dict)
async def get_asset_classification_register(
    register_request: npa_schemas.AssetClassificationRegisterRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Generate Asset Classification Register
    Shows all loans classified by NPA category
    """
    try:
        register = await service.generate_asset_classification_register(
            as_of_date=register_request.as_of_date,
            category_filter=register_request.category_filter
        )
        
        return success_response(data=register)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary", response_model=dict)
async def get_npa_summary(
    as_of_date: Optional[date] = Query(None),
    service: NPAService = Depends(get_npa_service)
):
    """
    Get summary of NPA statistics
    """
    try:
        if as_of_date is None:
            as_of_date = date.today()
        
        summary = await service.get_npa_summary(as_of_date=as_of_date)
        
        return success_response(data=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# NPA Movement Report Endpoints
# ============================================================================

@router.post("/movement-report", response_model=dict)
async def get_npa_movement_report(
    movement_request: npa_schemas.NPAMovementReportRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Generate NPA Movement Report
    Shows movement of accounts between categories during a period
    """
    try:
        movement_report = await service.generate_npa_movement_report(
            from_date=movement_request.from_date,
            to_date=movement_request.to_date
        )
        
        return success_response(data=movement_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vintage-analysis", response_model=dict)
async def get_vintage_analysis(
    vintage_request: npa_schemas.VintageAnalysisRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Generate Vintage Analysis Report
    Shows NPA rates by loan origination cohorts
    """
    try:
        vintage_report = await service.generate_vintage_analysis(
            as_of_date=vintage_request.as_of_date,
            cohort_by=vintage_request.cohort_by
        )
        
        return success_response(data=vintage_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Regulatory Report Endpoints
# ============================================================================

@router.post("/reports/rbi-return", response_model=dict)
async def get_rbi_npa_return(
    rbi_request: npa_schemas.RBINPAReturnRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Generate NPA return as per RBI format
    """
    try:
        rbi_report = await service.generate_rbi_npa_return(
            as_of_date=rbi_request.as_of_date
        )
        
        return success_response(data=rbi_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reports/provisioning-coverage-ratio", response_model=dict)
async def get_provisioning_coverage_ratio(
    pcr_request: npa_schemas.ProvisioningCoverageRatioRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Calculate Provisioning Coverage Ratio (PCR)
    PCR = (Provisions Held / Gross NPAs) * 100
    """
    try:
        pcr_report = await service.generate_provisioning_coverage_ratio(
            as_of_date=pcr_request.as_of_date
        )
        
        return success_response(data=pcr_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Batch Processing Endpoints
# ============================================================================

@router.post("/batch/monthly-classification", response_model=dict)
async def run_monthly_npa_classification(
    classification_request: npa_schemas.MonthlyNPAClassificationRequest,
    service: NPAService = Depends(get_npa_service)
):
    """
    Run monthly NPA classification for entire portfolio
    Creates provisioning entries for all loans
    """
    try:
        result = await service.run_monthly_npa_classification(
            as_of_date=classification_request.as_of_date
        )
        
        return success_response(
            data=result,
            message="Monthly NPA classification completed successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
