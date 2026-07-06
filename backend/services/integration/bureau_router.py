"""
Bureau Integration API Router
Endpoints for credit bureau operations

Features:
- Pull credit reports
- View report history
- Manage consents
- Multi-bureau support
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .bureau_manager import BureauManager

router = APIRouter(prefix="/api/v1/bureau", tags=["Bureau Integration"])


# Schemas
class ConsentCreate(BaseModel):
    customer_id: int
    consent_type: str = "credit_report"
    valid_days: int = Field(90, ge=1, le=365)


class BureauPullRequest(BaseModel):
    customer_id: int
    customer_data: dict
    bureau_name: Optional[str] = None
    fallback: bool = True


class MultiBureauPullRequest(BaseModel):
    customer_id: int
    customer_data: dict
    bureau_names: Optional[List[str]] = None


# Endpoints
@router.post("/consent")
async def create_consent(
    request: ConsentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create bureau consent for customer
    
    Required before pulling credit reports
    """
    try:
        bureau_manager = BureauManager(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('bureau_config', {})
        )
        
        consent = bureau_manager.create_consent(
            customer_id=request.customer_id,
            consent_type=request.consent_type,
            valid_days=request.valid_days
        )
        
        return {
            'success': True,
            'consent_id': consent.id,
            'valid_until': consent.valid_until.isoformat(),
            'message': 'Consent created successfully'
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pull-report")
async def pull_credit_report(
    request: BureauPullRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Pull credit report from bureau
    
    Automatically tries fallback bureaus if primary fails
    """
    try:
        bureau_manager = BureauManager(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('bureau_config', {})
        )
        
        result = bureau_manager.pull_credit_report(
            customer_id=request.customer_id,
            customer_data=request.customer_data,
            bureau_name=request.bureau_name,
            fallback=request.fallback
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pull-multi-bureau")
async def pull_multi_bureau(
    request: MultiBureauPullRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Pull reports from multiple bureaus simultaneously
    
    Returns combined results with average score
    """
    try:
        bureau_manager = BureauManager(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('bureau_config', {})
        )
        
        result = bureau_manager.pull_multi_bureau(
            customer_id=request.customer_id,
            customer_data=request.customer_data,
            bureau_names=request.bureau_names
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reports/{customer_id}")
async def get_report_history(
    customer_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get bureau report history for customer"""
    try:
        bureau_manager = BureauManager(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('bureau_config', {})
        )
        
        history = bureau_manager.get_report_history(
            customer_id=customer_id,
            limit=limit
        )
        
        return {
            'customer_id': customer_id,
            'reports': history
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/latest/{customer_id}")
async def get_latest_report(
    customer_id: int,
    bureau_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get latest credit report for customer"""
    try:
        bureau_manager = BureauManager(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('bureau_config', {})
        )
        
        report = bureau_manager.get_latest_report(
            customer_id=customer_id,
            bureau_name=bureau_name
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="No bureau report found")
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
