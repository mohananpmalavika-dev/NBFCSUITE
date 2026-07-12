"""
AML/CFT Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from uuid import UUID

from backend.shared.database.session import get_db
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from backend.shared.database.models import User

from backend.services.aml import (
    TransactionMonitoringService,
    AMLAlertService,
    CTRService,
    STRService,
    PEPScreeningService,
    SanctionScreeningService
)

from backend.services.aml.schemas import (
    # Transaction Monitoring
    TransactionMonitoringCreate,
    TransactionMonitoringResponse,
    TransactionMonitoringFilter,
    MonitoringRuleCreate,
    MonitoringRuleUpdate,
    MonitoringRuleResponse,
    
    # Alerts
    AMLAlertCreate,
    AMLAlertResponse,
    AMLAlertAssignment,
    AMLAlertReview,
    AMLAlertClose,
    
    # CTR
    CTRReportCreate,
    CTRReportResponse,
    CTRBulkSubmit,
    
    # STR
    STRReportCreate,
    STRReportUpdate,
    STRReportResponse,
    STRReportApproval,
    STRFIUSubmission,
    
    # PEP
    PEPScreeningCreate,
    PEPScreeningUpdate,
    PEPScreeningResponse,
    PEPEDDCompletion,
    
    # Sanctions
    SanctionListCreate,
    SanctionListResponse,
    SanctionScreeningCreate,
    SanctionScreeningUpdate,
    SanctionScreeningResponse,
    
    # Analytics
    AMLDashboardStats,
)


router = APIRouter(prefix="/aml", tags=["AML/CFT"])


# ============================================================================
# TRANSACTION MONITORING ENDPOINTS
# ============================================================================

@router.post("/transaction-monitoring", response_model=TransactionMonitoringResponse)
def monitor_transaction(
    data: TransactionMonitoringCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Monitor a transaction for AML/CFT"""
    service = TransactionMonitoringService(db, tenant_id)
    transaction = service.monitor_transaction(data, current_user.id)
    return transaction


@router.get("/transaction-monitoring", response_model=List[TransactionMonitoringResponse])
def list_transactions(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    customer_id: Optional[UUID] = None,
    risk_level: Optional[str] = None,
    requires_review: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List transaction monitoring records"""
    service = TransactionMonitoringService(db, tenant_id)
    filters = TransactionMonitoringFilter(
        start_date=start_date,
        end_date=end_date,
        customer_id=customer_id,
        risk_level=risk_level,
        requires_review=requires_review
    )
    return service.list_transactions(filters, skip, limit)


@router.get("/transaction-monitoring/{transaction_id}", response_model=TransactionMonitoringResponse)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get transaction monitoring details"""
    service = TransactionMonitoringService(db, tenant_id)
    transaction = service.get_transaction_monitoring(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/monitoring-rules", response_model=MonitoringRuleResponse)
def create_monitoring_rule(
    data: MonitoringRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create AML monitoring rule"""
    from backend.shared.database.aml_models import AMLMonitoringRule
    from uuid import uuid4
    
    rule = AMLMonitoringRule(
        id=uuid4(),
        tenant_id=tenant_id,
        **data.dict(),
        created_by=current_user.id
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


# ============================================================================
# ALERT ENDPOINTS
# ============================================================================

@router.get("/alerts", response_model=List[AMLAlertResponse])
def list_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List AML alerts"""
    service = AMLAlertService(db, tenant_id)
    return service.list_alerts(status, severity, assigned_to, customer_id, None, None, skip, limit)


@router.get("/alerts/{alert_id}", response_model=AMLAlertResponse)
def get_alert(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get alert details"""
    service = AMLAlertService(db, tenant_id)
    alert = service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/assign", response_model=AMLAlertResponse)
def assign_alert(
    alert_id: UUID,
    data: AMLAlertAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Assign alert to user"""
    service = AMLAlertService(db, tenant_id)
    alert = service.assign_alert(alert_id, data.assigned_to, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/review", response_model=AMLAlertResponse)
def review_alert(
    alert_id: UUID,
    data: AMLAlertReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Review alert"""
    service = AMLAlertService(db, tenant_id)
    alert = service.review_alert(alert_id, data, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/alerts/{alert_id}/close", response_model=AMLAlertResponse)
def close_alert(
    alert_id: UUID,
    data: AMLAlertClose,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Close alert"""
    service = AMLAlertService(db, tenant_id)
    alert = service.close_alert(alert_id, data, current_user.id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


# ============================================================================
# CTR ENDPOINTS
# ============================================================================

@router.post("/ctr", response_model=CTRReportResponse)
def create_ctr(
    data: CTRReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create CTR report"""
    service = CTRService(db, tenant_id)
    return service.create_ctr_report(data, current_user.id)


@router.get("/ctr", response_model=List[CTRReportResponse])
def list_ctrs(
    reporting_month: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List CTR reports"""
    service = CTRService(db, tenant_id)
    return service.list_ctr_reports(reporting_month, status, None, None, None, None, skip, limit)


@router.get("/ctr/{ctr_id}", response_model=CTRReportResponse)
def get_ctr(
    ctr_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get CTR report"""
    service = CTRService(db, tenant_id)
    ctr = service.get_ctr_report(ctr_id)
    if not ctr:
        raise HTTPException(status_code=404, detail="CTR report not found")
    return ctr


@router.post("/ctr/{ctr_id}/approve", response_model=CTRReportResponse)
def approve_ctr(
    ctr_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve CTR report"""
    service = CTRService(db, tenant_id)
    ctr = service.approve_ctr_report(ctr_id, current_user.id)
    if not ctr:
        raise HTTPException(status_code=404, detail="CTR report not found")
    return ctr


@router.post("/ctr/auto-generate")
def auto_generate_ctrs(
    reporting_month: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Auto-generate CTR reports for a month"""
    service = CTRService(db, tenant_id)
    return service.auto_generate_ctrs_for_month(reporting_month, current_user.id)


# ============================================================================
# STR ENDPOINTS
# ============================================================================

@router.post("/str", response_model=STRReportResponse)
def create_str(
    data: STRReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create STR report"""
    service = STRService(db, tenant_id)
    return service.create_str_report(data, current_user.id)


@router.get("/str", response_model=List[STRReportResponse])
def list_strs(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List STR reports"""
    service = STRService(db, tenant_id)
    return service.list_str_reports(status, None, None, None, None, skip, limit)


@router.get("/str/{str_id}", response_model=STRReportResponse)
def get_str(
    str_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get STR report"""
    service = STRService(db, tenant_id)
    str_report = service.get_str_report(str_id)
    if not str_report:
        raise HTTPException(status_code=404, detail="STR report not found")
    return str_report


@router.put("/str/{str_id}", response_model=STRReportResponse)
def update_str(
    str_id: UUID,
    data: STRReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update STR report"""
    service = STRService(db, tenant_id)
    str_report = service.update_str_report(str_id, data, current_user.id)
    if not str_report:
        raise HTTPException(status_code=404, detail="STR report not found")
    return str_report


@router.post("/str/{str_id}/approve", response_model=STRReportResponse)
def approve_str(
    str_id: UUID,
    data: STRReportApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Approve STR report"""
    service = STRService(db, tenant_id)
    str_report = service.approve_str_report(str_id, data, current_user.id)
    if not str_report:
        raise HTTPException(status_code=404, detail="STR report not found")
    return str_report


@router.post("/str/{str_id}/submit-fiu", response_model=STRReportResponse)
def submit_str_to_fiu(
    str_id: UUID,
    data: STRFIUSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Submit STR to FIU"""
    service = STRService(db, tenant_id)
    str_report = service.submit_to_fiu(str_id, data, current_user.id)
    if not str_report:
        raise HTTPException(status_code=404, detail="STR report not found")
    return str_report


# ============================================================================
# PEP SCREENING ENDPOINTS
# ============================================================================

@router.post("/pep-screening", response_model=PEPScreeningResponse)
def create_pep_screening(
    data: PEPScreeningCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create PEP screening"""
    service = PEPScreeningService(db, tenant_id)
    return service.create_screening(data, current_user.id)


@router.get("/pep-screening", response_model=List[PEPScreeningResponse])
def list_pep_screenings(
    customer_id: Optional[UUID] = None,
    is_pep: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List PEP screenings"""
    service = PEPScreeningService(db, tenant_id)
    return service.list_screenings(customer_id, None, is_pep, None, skip, limit)


@router.get("/pep-screening/{screening_id}", response_model=PEPScreeningResponse)
def get_pep_screening(
    screening_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get PEP screening"""
    service = PEPScreeningService(db, tenant_id)
    screening = service.get_screening(screening_id)
    if not screening:
        raise HTTPException(status_code=404, detail="PEP screening not found")
    return screening


@router.put("/pep-screening/{screening_id}", response_model=PEPScreeningResponse)
def update_pep_screening(
    screening_id: UUID,
    data: PEPScreeningUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update PEP screening"""
    service = PEPScreeningService(db, tenant_id)
    screening = service.update_screening(screening_id, data, current_user.id)
    if not screening:
        raise HTTPException(status_code=404, detail="PEP screening not found")
    return screening


@router.post("/pep-screening/{screening_id}/complete-edd", response_model=PEPScreeningResponse)
def complete_edd(
    screening_id: UUID,
    data: PEPEDDCompletion,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Complete Enhanced Due Diligence"""
    service = PEPScreeningService(db, tenant_id)
    screening = service.complete_edd(screening_id, data, current_user.id)
    if not screening:
        raise HTTPException(status_code=404, detail="PEP screening not found")
    return screening


# ============================================================================
# SANCTION SCREENING ENDPOINTS
# ============================================================================

@router.post("/sanction-lists", response_model=SanctionListResponse)
def create_sanction_list_entry(
    data: SanctionListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Add entry to sanction list"""
    service = SanctionScreeningService(db, tenant_id)
    return service.create_sanction_list_entry(data, current_user.id)


@router.get("/sanction-lists", response_model=List[SanctionListResponse])
def list_sanction_lists(
    list_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List sanction list entries"""
    service = SanctionScreeningService(db, tenant_id)
    return service.list_sanction_entries(list_type, is_active, None, skip, limit)


@router.post("/sanction-screening", response_model=SanctionScreeningResponse)
def create_sanction_screening(
    data: SanctionScreeningCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create sanction screening"""
    service = SanctionScreeningService(db, tenant_id)
    return service.create_screening(data, current_user.id)


@router.get("/sanction-screening", response_model=List[SanctionScreeningResponse])
def list_sanction_screenings(
    customer_id: Optional[UUID] = None,
    is_match_found: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """List sanction screenings"""
    service = SanctionScreeningService(db, tenant_id)
    return service.list_screenings(customer_id, None, is_match_found, None, skip, limit)


@router.get("/sanction-screening/{screening_id}", response_model=SanctionScreeningResponse)
def get_sanction_screening(
    screening_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get sanction screening"""
    service = SanctionScreeningService(db, tenant_id)
    screening = service.get_screening(screening_id)
    if not screening:
        raise HTTPException(status_code=404, detail="Sanction screening not found")
    return screening


@router.put("/sanction-screening/{screening_id}", response_model=SanctionScreeningResponse)
def update_sanction_screening(
    screening_id: UUID,
    data: SanctionScreeningUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update sanction screening"""
    service = SanctionScreeningService(db, tenant_id)
    screening = service.update_screening(screening_id, data, current_user.id)
    if not screening:
        raise HTTPException(status_code=404, detail="Sanction screening not found")
    return screening


# ============================================================================
# DASHBOARD & ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/dashboard", response_model=AMLDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get AML dashboard statistics"""
    txn_service = TransactionMonitoringService(db, tenant_id)
    alert_service = AMLAlertService(db, tenant_id)
    ctr_service = CTRService(db, tenant_id)
    str_service = STRService(db, tenant_id)
    pep_service = PEPScreeningService(db, tenant_id)
    sanction_service = SanctionScreeningService(db, tenant_id)
    
    txn_stats = txn_service.get_transaction_statistics()
    alert_stats = alert_service.get_alert_statistics()
    ctr_stats = ctr_service.get_ctr_statistics()
    str_stats = str_service.get_str_statistics()
    pep_stats = pep_service.get_pep_statistics()
    sanction_stats = sanction_service.get_sanction_statistics()
    
    return AMLDashboardStats(
        total_transactions_monitored=txn_stats['total_transactions'],
        high_risk_transactions=txn_stats['high_risk_count'] + txn_stats['critical_risk_count'],
        cash_transactions=txn_stats['cash_transactions'],
        cross_border_transactions=txn_stats['cross_border_transactions'],
        total_alerts=alert_stats['total_alerts'],
        open_alerts=alert_stats['open_alerts'],
        under_review_alerts=alert_stats['under_review'],
        escalated_alerts=alert_stats['escalated'],
        closed_alerts=alert_stats['total_alerts'] - alert_stats['open_alerts'] - alert_stats['under_review'] - alert_stats['escalated'],
        total_ctr_reports=ctr_stats['total_reports'],
        pending_ctr_reports=ctr_stats['draft'] + ctr_stats['pending_review'],
        submitted_ctr_reports=ctr_stats['submitted'],
        total_str_reports=str_stats['total_reports'],
        pending_str_reports=str_stats['draft'] + str_stats['pending_review'],
        submitted_str_reports=str_stats['submitted'],
        total_pep_screenings=pep_stats['total_screenings'],
        confirmed_peps=pep_stats['confirmed_peps'],
        total_sanction_screenings=sanction_stats['total_screenings'],
        sanction_matches=sanction_stats['confirmed_matches'],
        alerts_by_type=alert_stats['alerts_by_type'],
        transactions_by_risk={}
    )
