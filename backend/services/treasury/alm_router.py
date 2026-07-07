"""
ALM (Asset Liability Management) Router
API endpoints for maturity ladder, gap analysis, liquidity ratios, interest rate risk
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.shared.database.connection import get_db
from backend.services.auth.dependencies import get_current_user
from backend.shared.database.models import User
from backend.shared.database.alm_models import RiskLevel, GapType, InterestRateScenario

from . import alm_schemas as schemas
from .alm_service import (
    MaturityLadderService,
    GapAnalysisService,
    LiquidityRatioService,
    InterestRateRiskService,
    QuarterlyReturnService,
    ALMAlertService,
    ALMDashboardService
)

router = APIRouter(prefix="/api/treasury/alm", tags=["ALM"])


# ============================================================================
# Maturity Ladder Endpoints
# ============================================================================

@router.post("/maturity-ladder", response_model=schemas.MaturityLadderResponse)
def create_maturity_ladder(
    data: schemas.MaturityLadderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create maturity ladder entry"""
    service = MaturityLadderService(db, current_user.tenant_id, current_user.id)
    return service.create_maturity_ladder(data)


@router.get("/maturity-ladder/{report_date}", response_model=schemas.MaturityLadderListResponse)
def get_maturity_ladder(
    report_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maturity ladder for specific date"""
    service = MaturityLadderService(db, current_user.tenant_id, current_user.id)
    entries = service.get_maturity_ladder(report_date)
    
    if not entries:
        raise HTTPException(status_code=404, detail="No maturity ladder data found")
    
    total_assets = sum(e.total_assets for e in entries)
    total_liabilities = sum(e.total_liabilities for e in entries)
    net_gap = total_assets - total_liabilities
    
    return schemas.MaturityLadderListResponse(
        entries=entries,
        total=len(entries),
        report_date=report_date,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_gap=net_gap
    )


@router.get("/maturity-ladder/{report_date}/summary", response_model=schemas.MaturityLadderSummary)
def get_maturity_ladder_summary(
    report_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maturity ladder summary"""
    service = MaturityLadderService(db, current_user.tenant_id, current_user.id)
    return service.get_maturity_ladder_summary(report_date)


@router.put("/maturity-ladder/{entry_id}", response_model=schemas.MaturityLadderResponse)
def update_maturity_ladder(
    entry_id: int,
    data: schemas.MaturityLadderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maturity ladder entry"""
    service = MaturityLadderService(db, current_user.tenant_id, current_user.id)
    return service.update_maturity_ladder(entry_id, data)


# ============================================================================
# Gap Analysis Endpoints
# ============================================================================

@router.post("/gap-analysis", response_model=schemas.GapAnalysisResponse)
def create_gap_analysis(
    data: schemas.GapAnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create gap analysis entry"""
    service = GapAnalysisService(db, current_user.tenant_id, current_user.id)
    return service.create_gap_analysis(data)


@router.get("/gap-analysis/{report_date}/{analysis_type}", response_model=schemas.GapAnalysisListResponse)
def get_gap_analysis(
    report_date: date,
    analysis_type: GapType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get gap analysis for specific date and type"""
    service = GapAnalysisService(db, current_user.tenant_id, current_user.id)
    entries = service.get_gap_analysis(report_date, analysis_type)
    
    return schemas.GapAnalysisListResponse(
        entries=entries,
        total=len(entries),
        report_date=report_date,
        analysis_type=analysis_type
    )


@router.get("/gap-analysis/{report_date}/{analysis_type}/summary", 
            response_model=schemas.GapAnalysisSummary)
def get_gap_analysis_summary(
    report_date: date,
    analysis_type: GapType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get gap analysis summary"""
    service = GapAnalysisService(db, current_user.tenant_id, current_user.id)
    return service.get_gap_analysis_summary(report_date, analysis_type)


# ============================================================================
# Liquidity Ratio Endpoints
# ============================================================================

@router.post("/liquidity-ratios", response_model=schemas.LiquidityRatioResponse)
def create_liquidity_ratio(
    data: schemas.LiquidityRatioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create liquidity ratio entry"""
    service = LiquidityRatioService(db, current_user.tenant_id, current_user.id)
    return service.create_liquidity_ratio(data)


@router.get("/liquidity-ratios/{report_date}", response_model=schemas.LiquidityRatioResponse)
def get_liquidity_ratio(
    report_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get liquidity ratio for specific date"""
    service = LiquidityRatioService(db, current_user.tenant_id, current_user.id)
    return service.get_liquidity_ratio(report_date)


@router.get("/liquidity-ratios/trends/{metric_name}", response_model=schemas.LiquidityRatioTrend)
def get_liquidity_trends(
    metric_name: str,
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get liquidity ratio trends"""
    service = LiquidityRatioService(db, current_user.tenant_id, current_user.id)
    return service.get_liquidity_trends(start_date, end_date, metric_name)


# ============================================================================
# Interest Rate Risk Endpoints
# ============================================================================

@router.post("/interest-rate-risk", response_model=schemas.InterestRateRiskResponse)
def create_interest_rate_risk(
    data: schemas.InterestRateRiskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create interest rate risk analysis"""
    service = InterestRateRiskService(db, current_user.tenant_id, current_user.id)
    return service.create_interest_rate_risk(data)


@router.get("/interest-rate-risk/{report_date}", response_model=schemas.InterestRateRiskListResponse)
def get_interest_rate_risk(
    report_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all interest rate risk scenarios"""
    service = InterestRateRiskService(db, current_user.tenant_id, current_user.id)
    entries = service.get_interest_rate_risk(report_date)
    
    return schemas.InterestRateRiskListResponse(
        entries=entries,
        total=len(entries),
        report_date=report_date
    )


@router.get("/interest-rate-risk/{report_date}/summary", 
            response_model=schemas.InterestRateRiskSummary)
def get_irr_summary(
    report_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get interest rate risk summary"""
    service = InterestRateRiskService(db, current_user.tenant_id, current_user.id)
    return service.get_irr_summary(report_date)


# ============================================================================
# Quarterly Return Endpoints
# ============================================================================

@router.post("/quarterly-returns", response_model=schemas.QuarterlyReturnResponse)
def create_quarterly_return(
    data: schemas.QuarterlyReturnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create quarterly ALM return"""
    service = QuarterlyReturnService(db, current_user.tenant_id, current_user.id)
    return service.create_quarterly_return(data)


@router.get("/quarterly-returns/{year}/{quarter}", response_model=schemas.QuarterlyReturnResponse)
def get_quarterly_return(
    year: int,
    quarter: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific quarterly return"""
    service = QuarterlyReturnService(db, current_user.tenant_id, current_user.id)
    return service.get_quarterly_return(year, quarter)


@router.get("/quarterly-returns", response_model=schemas.QuarterlyReturnListResponse)
def list_quarterly_returns(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all quarterly returns"""
    service = QuarterlyReturnService(db, current_user.tenant_id, current_user.id)
    returns = service.list_quarterly_returns(skip, limit)
    
    return schemas.QuarterlyReturnListResponse(
        returns=returns,
        total=len(returns)
    )


@router.post("/quarterly-returns/{return_id}/approve", response_model=schemas.QuarterlyReturnResponse)
def approve_quarterly_return(
    return_id: int,
    approval_data: schemas.QuarterlyReturnApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve quarterly return"""
    service = QuarterlyReturnService(db, current_user.tenant_id, current_user.id)
    return service.approve_quarterly_return(return_id, approval_data)


@router.post("/quarterly-returns/{return_id}/file", response_model=schemas.QuarterlyReturnResponse)
def file_quarterly_return(
    return_id: int,
    filing_data: schemas.QuarterlyReturnFiling,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """File quarterly return with regulator"""
    service = QuarterlyReturnService(db, current_user.tenant_id, current_user.id)
    return service.file_quarterly_return(return_id, filing_data)


# ============================================================================
# Alert Endpoints
# ============================================================================

@router.get("/alerts", response_model=schemas.ALMAlertListResponse)
def list_alerts(
    is_resolved: Optional[bool] = None,
    severity: Optional[RiskLevel] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List ALM alerts"""
    service = ALMAlertService(db, current_user.tenant_id, current_user.id)
    alerts = service.list_alerts(is_resolved, severity, skip, limit)
    
    unresolved_count = len([a for a in alerts if not a.is_resolved])
    critical_count = len([a for a in alerts if a.severity == RiskLevel.CRITICAL and not a.is_resolved])
    
    return schemas.ALMAlertListResponse(
        alerts=alerts,
        total=len(alerts),
        unresolved_count=unresolved_count,
        critical_count=critical_count
    )


@router.post("/alerts/{alert_id}/acknowledge", response_model=schemas.ALMAlertResponse)
def acknowledge_alert(
    alert_id: int,
    data: schemas.ALMAlertAcknowledge,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge an alert"""
    service = ALMAlertService(db, current_user.tenant_id, current_user.id)
    return service.acknowledge_alert(alert_id, data.notes)


@router.post("/alerts/{alert_id}/resolve", response_model=schemas.ALMAlertResponse)
def resolve_alert(
    alert_id: int,
    data: schemas.ALMAlertResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve an alert"""
    service = ALMAlertService(db, current_user.tenant_id, current_user.id)
    return service.resolve_alert(alert_id, data.resolution_notes)


# ============================================================================
# Dashboard Endpoint
# ============================================================================

@router.get("/dashboard/{as_of_date}", response_model=schemas.ALMDashboard)
def get_alm_dashboard(
    as_of_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive ALM dashboard"""
    service = ALMDashboardService(db, current_user.tenant_id, current_user.id)
    return service.get_dashboard(as_of_date)
