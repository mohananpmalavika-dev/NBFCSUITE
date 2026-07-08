"""
Insurance Claim Router

API endpoints for claims processing including:
- Claim registration and tracking
- Assessment and approval workflow
- Document management
- Settlement processing
- Statistics
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.services.insurance.claim_service import ClaimService
from backend.services.insurance.schemas import (
    InsuranceClaimCreate,
    InsuranceClaimResponse,
    InsuranceClaimAssessment,
    InsuranceClaimApproval,
    InsuranceClaimRejection,
    InsuranceClaimSettlement,
    ClaimFilter,
    ClaimStatistics,
    ClaimStatus,
    ClaimType
)

router = APIRouter(prefix="/insurance/claims", tags=["Insurance - Claims"])


# ==================== CRUD OPERATIONS ====================

@router.post("", response_model=dict, status_code=201)
async def create_claim(
    claim_data: InsuranceClaimCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Register new insurance claim
    
    - **policy_id**: Policy UUID
    - **claim_type**: death, maturity, health, accident, etc.
    - **claim_amount**: Claimed amount
    - **incident_date**: Date of incident
    - **incident_description**: Detailed description
    - **claimant_name**: Name of person claiming
    
    Returns created claim with generated claim number
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.create_claim(claim_data.dict())
    
    return success_response(
        message="Insurance claim registered successfully",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


@router.get("", response_model=dict)
async def list_claims(
    policy_id: Optional[uuid.UUID] = Query(None, description="Filter by policy"),
    claim_type: Optional[ClaimType] = Query(None, description="Filter by claim type"),
    claim_status: Optional[ClaimStatus] = Query(None, description="Filter by status"),
    from_claimed_date: Optional[datetime] = Query(None, description="From claimed date"),
    to_claimed_date: Optional[datetime] = Query(None, description="To claimed date"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    List all claims with optional filters
    
    - **policy_id**: Filter by specific policy
    - **claim_type**: death, maturity, health, etc.
    - **claim_status**: registered, under_review, approved, settled, etc.
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claims = service.list_claims(
        policy_id=policy_id,
        claim_type=claim_type,
        claim_status=claim_status,
        from_claimed_date=from_claimed_date,
        to_claimed_date=to_claimed_date,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(claims)} claims",
        data={
            "claims": [InsuranceClaimResponse.from_orm(c).dict() for c in claims],
            "total": len(claims),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{claim_id}", response_model=dict)
async def get_claim(
    claim_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get claim by ID"""
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.get_claim(claim_id)
    
    return success_response(
        message="Claim retrieved successfully",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


@router.get("/number/{claim_number}", response_model=dict)
async def get_claim_by_number(
    claim_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get claim by claim number"""
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.get_claim_by_number(claim_number)
    
    return success_response(
        message="Claim retrieved successfully",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


# ==================== WORKFLOW OPERATIONS ====================

@router.post("/{claim_id}/review", response_model=dict)
async def mark_under_review(
    claim_id: uuid.UUID,
    remarks: Optional[str] = Query(None, description="Review remarks"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Mark claim as under review
    
    First step in claim processing workflow
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.mark_under_review(claim_id, remarks)
    
    return success_response(
        message="Claim marked as under review",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


@router.post("/{claim_id}/documents-pending", response_model=dict)
async def mark_documents_pending(
    claim_id: uuid.UUID,
    remarks: Optional[str] = Query(None, description="Remarks about pending documents"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Mark claim as documents pending
    
    Use when additional documentation is required
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.mark_documents_pending(claim_id, remarks)
    
    return success_response(
        message="Claim marked as documents pending",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


@router.post("/{claim_id}/assess", response_model=dict)
async def assess_claim(
    claim_id: uuid.UUID,
    assessment_data: InsuranceClaimAssessment,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Assess claim and determine eligible amount
    
    - **assessed_amount**: Amount determined as eligible
    - **assessment_remarks**: Detailed assessment notes
    - **documents_verified**: Whether all documents are verified
    - **deductions**: Any deductions to be applied
    - **investigation_status**: If investigation is required
    
    This determines the actual payable amount after verification
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.assess_claim(claim_id, assessment_data.dict())
    
    return success_response(
        message="Claim assessed successfully",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


@router.post("/{claim_id}/approve", response_model=dict)
async def approve_claim(
    claim_id: uuid.UUID,
    approval_data: InsuranceClaimApproval,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Approve assessed claim for settlement
    
    - **approved_amount**: Final approved amount
    - **approval_remarks**: Approval notes
    - **target_settlement_date**: Expected settlement date
    
    Only assessed claims can be approved
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.approve_claim(claim_id, approval_data.dict())
    
    return success_response(
        message="Claim approved successfully",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


@router.post("/{claim_id}/reject", response_model=dict)
async def reject_claim(
    claim_id: uuid.UUID,
    rejection_data: InsuranceClaimRejection,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Reject claim with reason
    
    - **rejection_reason**: Detailed reason for rejection
    
    Rejected claims cannot be processed further
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.reject_claim(claim_id, rejection_data.dict())
    
    return success_response(
        message="Claim rejected",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


@router.post("/{claim_id}/settle", response_model=dict)
async def settle_claim(
    claim_id: uuid.UUID,
    settlement_data: InsuranceClaimSettlement,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Settle approved claim
    
    - **settlement_amount**: Amount being paid
    - **settlement_method**: cheque, neft, rtgs, cash
    - **settlement_reference**: Payment reference number
    - **settlement_remarks**: Settlement notes
    
    Final step - marks claim as settled and complete
    Calculates total processing days
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    claim = service.settle_claim(claim_id, settlement_data.dict())
    
    return success_response(
        message="Claim settled successfully",
        data=InsuranceClaimResponse.from_orm(claim).dict()
    )


# ==================== STATISTICS ====================

@router.get("/stats/summary", response_model=dict)
async def get_claim_statistics(
    policy_id: Optional[uuid.UUID] = Query(None, description="Filter by policy"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get comprehensive claim statistics
    
    Returns:
    - Total claims by status and type
    - Claimed, assessed, approved, and settled amounts
    - Average processing time
    - Settlement rate
    
    Can be filtered by specific policy
    """
    service = ClaimService(db, tenant_id, current_user["id"])
    stats = service.get_claim_statistics(policy_id=policy_id)
    
    return success_response(
        message="Claim statistics retrieved successfully",
        data=stats
    )
