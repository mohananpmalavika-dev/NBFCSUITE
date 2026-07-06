"""
Bank Statement Analysis API Router
Endpoints for bank statement analysis and income verification

Features:
- Upload and analyze bank statements
- View analysis results
- Income verification reports
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from .bank_statement_service import BankStatementService

router = APIRouter(prefix="/api/v1/bank-statement", tags=["Bank Statement Analysis"])


# Schemas
class AnalyzeStatementRequest(BaseModel):
    customer_id: int
    statement_file_url: str
    application_id: Optional[int] = None
    password: Optional[str] = None


# Endpoints
@router.post("/analyze")
async def analyze_bank_statement(
    request: AnalyzeStatementRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze bank statement
    
    Triggers automated analysis using Perfios/FinBox
    Returns income verification, risk indicators, and banking behavior
    """
    try:
        service = BankStatementService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('bank_statement_config', {})
        )
        
        result = service.analyze_statement(
            customer_id=request.customer_id,
            statement_file_url=request.statement_file_url,
            application_id=request.application_id,
            password=request.password
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analysis/{customer_id}")
async def get_latest_analysis(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get latest bank statement analysis for customer"""
    try:
        service = BankStatementService(
            db=db,
            tenant_id=current_user['tenant_id'],
            config=current_user.get('bank_statement_config', {})
        )
        
        analysis = service.get_latest_analysis(customer_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="No bank statement analysis found")
        
        return {
            'analysis_id': analysis.id,
            'customer_id': customer_id,
            'bank_name': analysis.bank_name,
            'statement_period': {
                'from': analysis.statement_period_from.isoformat() if analysis.statement_period_from else None,
                'to': analysis.statement_period_to.isoformat() if analysis.statement_period_to else None
            },
            'income': {
                'avg_monthly_income': float(analysis.avg_monthly_income or 0),
                'salary_credits_count': analysis.salary_credits_count,
                'income_stability_score': analysis.income_stability_score,
                'irregular_income': analysis.irregular_income
            },
            'expenses': {
                'avg_monthly_expenses': float(analysis.avg_monthly_expenses or 0),
                'emi_obligations': float(analysis.emi_obligations or 0)
            },
            'banking_behavior': {
                'avg_balance': float(analysis.avg_balance or 0),
                'bounced_transactions': analysis.bounced_transactions or 0,
                'overdraft_instances': analysis.overdraft_instances or 0
            },
            'risk': {
                'risk_score': analysis.risk_score,
                'risk_level': analysis.risk_level,
                'red_flags': analysis.red_flags or []
            },
            'analyzed_at': analysis.analyzed_at.isoformat() if analysis.analyzed_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analysis/application/{application_id}")
async def get_analysis_by_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get bank statement analysis for specific loan application"""
    try:
        from backend.shared.database.integration_models import BankStatementAnalysis
        
        analysis = db.query(BankStatementAnalysis).filter(
            BankStatementAnalysis.application_id == application_id,
            BankStatementAnalysis.tenant_id == current_user['tenant_id'],
            BankStatementAnalysis.is_deleted == False
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="No analysis found for this application")
        
        return {
            'analysis_id': analysis.id,
            'application_id': application_id,
            'customer_id': analysis.customer_id,
            'avg_monthly_income': float(analysis.avg_monthly_income or 0),
            'income_stability_score': analysis.income_stability_score,
            'risk_score': analysis.risk_score,
            'risk_level': analysis.risk_level,
            'red_flags': analysis.red_flags or []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
