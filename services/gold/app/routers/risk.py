"""
Risk Management Router
Phase 11: Risk Management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

from ..database import get_db
from ..models.risk import (
    RiskParameter, CreditRiskAssessment, OperationalRiskEvent, MarketRiskExposure,
    ConcentrationRiskLimit, RiskAlert, RiskMitigation, RiskReport,
    RiskDashboard, ComplianceCheck
)
from ..schemas.risk import (
    RiskParameterCreate, RiskParameterUpdate, RiskParameterResponse,
    CreditRiskAssessmentCreate, CreditRiskAssessmentUpdate, CreditRiskAssessmentResponse,
    CreditRiskApprovalRequest, OperationalRiskEventCreate, OperationalRiskEventUpdate,
    OperationalRiskEventResponse, MarketRiskExposureCreate, MarketRiskExposureResponse,
    ConcentrationRiskLimitCreate, ConcentrationRiskLimitUpdate, ConcentrationRiskLimitResponse,
    ConcentrationRiskMonitorResponse, RiskAlertCreate, RiskAlertUpdate, RiskAlertResponse,
    RiskAlertResolveRequest, RiskMitigationCreate, RiskMitigationUpdate, RiskMitigationResponse,
    RiskMitigationApprovalRequest, RiskReportCreate, RiskReportUpdate, RiskReportResponse,
    RiskReportApprovalRequest, RiskReportPublishRequest, RiskDashboardCreate,
    RiskDashboardUpdate, RiskDashboardResponse, ComplianceCheckCreate, ComplianceCheckUpdate,
    ComplianceCheckResponse, ComplianceCheckReviewRequest, ComplianceCheckApprovalRequest,
    CreditRiskStatistics, OperationalRiskStatistics, MarketRiskStatistics,
    ConcentrationRiskStatistics, ComplianceStatistics
)

router = APIRouter(prefix="/api/v1/gold/risk", tags=["risk"])


# =====================================================
# Risk Parameters Endpoints
# =====================================================

@router.post("/parameters", response_model=RiskParameterResponse, status_code=201)
def create_risk_parameter(
    parameter: RiskParameterCreate,
    db: Session = Depends(get_db)
):
    """Create a new risk parameter"""
    # Check for duplicate parameter code
    existing = db.query(RiskParameter).filter(
        RiskParameter.parameter_code == parameter.parameter_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Parameter code already exists")
    
    db_parameter = RiskParameter(**parameter.model_dump())
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter


@router.get("/parameters", response_model=List[RiskParameterResponse])
def list_risk_parameters(
    risk_category: Optional[str] = None,
    parameter_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List risk parameters with filters"""
    query = db.query(RiskParameter)
    
    if risk_category:
        query = query.filter(RiskParameter.risk_category == risk_category)
    if parameter_type:
        query = query.filter(RiskParameter.parameter_type == parameter_type)
    if is_active is not None:
        query = query.filter(RiskParameter.is_active == is_active)
    
    query = query.order_by(RiskParameter.parameter_code)
    return query.offset(skip).limit(limit).all()


@router.get("/parameters/{parameter_id}", response_model=RiskParameterResponse)
def get_risk_parameter(parameter_id: UUID, db: Session = Depends(get_db)):
    """Get risk parameter by ID"""
    parameter = db.query(RiskParameter).filter(
        RiskParameter.parameter_id == parameter_id
    ).first()
    if not parameter:
        raise HTTPException(status_code=404, detail="Risk parameter not found")
    return parameter


@router.put("/parameters/{parameter_id}", response_model=RiskParameterResponse)
def update_risk_parameter(
    parameter_id: UUID,
    parameter: RiskParameterUpdate,
    db: Session = Depends(get_db)
):
    """Update risk parameter"""
    db_parameter = db.query(RiskParameter).filter(
        RiskParameter.parameter_id == parameter_id
    ).first()
    if not db_parameter:
        raise HTTPException(status_code=404, detail="Risk parameter not found")
    
    update_data = parameter.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_parameter, field, value)
    
    db.commit()
    db.refresh(db_parameter)
    return db_parameter


@router.delete("/parameters/{parameter_id}", status_code=204)
def delete_risk_parameter(parameter_id: UUID, db: Session = Depends(get_db)):
    """Delete risk parameter"""
    parameter = db.query(RiskParameter).filter(
        RiskParameter.parameter_id == parameter_id
    ).first()
    if not parameter:
        raise HTTPException(status_code=404, detail="Risk parameter not found")
    
    db.delete(parameter)
    db.commit()
    return None


# =====================================================
# Credit Risk Assessment Endpoints
# =====================================================

@router.post("/credit-assessments", response_model=CreditRiskAssessmentResponse, status_code=201)
def create_credit_risk_assessment(
    assessment: CreditRiskAssessmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new credit risk assessment"""
    db_assessment = CreditRiskAssessment(**assessment.model_dump())
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.get("/credit-assessments", response_model=List[CreditRiskAssessmentResponse])
def list_credit_risk_assessments(
    loan_id: Optional[UUID] = None,
    customer_id: Optional[UUID] = None,
    assessment_type: Optional[str] = None,
    risk_category: Optional[str] = None,
    approval_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List credit risk assessments with filters"""
    query = db.query(CreditRiskAssessment)
    
    if loan_id:
        query = query.filter(CreditRiskAssessment.loan_id == loan_id)
    if customer_id:
        query = query.filter(CreditRiskAssessment.customer_id == customer_id)
    if assessment_type:
        query = query.filter(CreditRiskAssessment.assessment_type == assessment_type)
    if risk_category:
        query = query.filter(CreditRiskAssessment.risk_category == risk_category)
    if approval_status:
        query = query.filter(CreditRiskAssessment.approval_status == approval_status)
    if date_from:
        query = query.filter(CreditRiskAssessment.assessment_date >= date_from)
    if date_to:
        query = query.filter(CreditRiskAssessment.assessment_date <= date_to)
    
    query = query.order_by(desc(CreditRiskAssessment.assessment_date))
    return query.offset(skip).limit(limit).all()


@router.get("/credit-assessments/{assessment_id}", response_model=CreditRiskAssessmentResponse)
def get_credit_risk_assessment(assessment_id: UUID, db: Session = Depends(get_db)):
    """Get credit risk assessment by ID"""
    assessment = db.query(CreditRiskAssessment).filter(
        CreditRiskAssessment.assessment_id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Credit risk assessment not found")
    return assessment


@router.put("/credit-assessments/{assessment_id}", response_model=CreditRiskAssessmentResponse)
def update_credit_risk_assessment(
    assessment_id: UUID,
    assessment: CreditRiskAssessmentUpdate,
    db: Session = Depends(get_db)
):
    """Update credit risk assessment"""
    db_assessment = db.query(CreditRiskAssessment).filter(
        CreditRiskAssessment.assessment_id == assessment_id
    ).first()
    if not db_assessment:
        raise HTTPException(status_code=404, detail="Credit risk assessment not found")
    
    if db_assessment.approval_status == 'approved':
        raise HTTPException(status_code=400, detail="Cannot update approved assessment")
    
    update_data = assessment.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_assessment, field, value)
    
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.post("/credit-assessments/{assessment_id}/approve", response_model=CreditRiskAssessmentResponse)
def approve_credit_risk_assessment(
    assessment_id: UUID,
    request: CreditRiskApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve credit risk assessment"""
    assessment = db.query(CreditRiskAssessment).filter(
        CreditRiskAssessment.assessment_id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Credit risk assessment not found")
    
    if assessment.approval_status == 'approved':
        raise HTTPException(status_code=400, detail="Assessment already approved")
    
    assessment.approval_status = 'approved'
    assessment.approved_by = request.approved_by
    assessment.approved_at = datetime.utcnow()
    assessment.approval_notes = request.approval_notes
    
    db.commit()
    db.refresh(assessment)
    return assessment


@router.delete("/credit-assessments/{assessment_id}", status_code=204)
def delete_credit_risk_assessment(assessment_id: UUID, db: Session = Depends(get_db)):
    """Delete credit risk assessment"""
    assessment = db.query(CreditRiskAssessment).filter(
        CreditRiskAssessment.assessment_id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Credit risk assessment not found")
    
    if assessment.approval_status == 'approved':
        raise HTTPException(status_code=403, detail="Cannot delete approved assessment")
    
    db.delete(assessment)
    db.commit()
    return None


# =====================================================
# Operational Risk Event Endpoints
# =====================================================

@router.post("/operational-events", response_model=OperationalRiskEventResponse, status_code=201)
def create_operational_risk_event(
    event: OperationalRiskEventCreate,
    db: Session = Depends(get_db)
):
    """Create a new operational risk event"""
    db_event = OperationalRiskEvent(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


@router.get("/operational-events", response_model=List[OperationalRiskEventResponse])
def list_operational_risk_events(
    event_category: Optional[str] = None,
    severity_level: Optional[str] = None,
    event_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List operational risk events with filters"""
    query = db.query(OperationalRiskEvent)
    
    if event_category:
        query = query.filter(OperationalRiskEvent.event_category == event_category)
    if severity_level:
        query = query.filter(OperationalRiskEvent.severity_level == severity_level)
    if event_status:
        query = query.filter(OperationalRiskEvent.event_status == event_status)
    if date_from:
        query = query.filter(OperationalRiskEvent.event_date >= date_from)
    if date_to:
        query = query.filter(OperationalRiskEvent.event_date <= date_to)
    
    query = query.order_by(desc(OperationalRiskEvent.event_date))
    return query.offset(skip).limit(limit).all()


@router.get("/operational-events/{event_id}", response_model=OperationalRiskEventResponse)
def get_operational_risk_event(event_id: UUID, db: Session = Depends(get_db)):
    """Get operational risk event by ID"""
    event = db.query(OperationalRiskEvent).filter(
        OperationalRiskEvent.event_id == event_id
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Operational risk event not found")
    return event


@router.put("/operational-events/{event_id}", response_model=OperationalRiskEventResponse)
def update_operational_risk_event(
    event_id: UUID,
    event: OperationalRiskEventUpdate,
    db: Session = Depends(get_db)
):
    """Update operational risk event"""
    db_event = db.query(OperationalRiskEvent).filter(
        OperationalRiskEvent.event_id == event_id
    ).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Operational risk event not found")
    
    update_data = event.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event


@router.delete("/operational-events/{event_id}", status_code=204)
def delete_operational_risk_event(event_id: UUID, db: Session = Depends(get_db)):
    """Delete operational risk event"""
    event = db.query(OperationalRiskEvent).filter(
        OperationalRiskEvent.event_id == event_id
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Operational risk event not found")
    
    db.delete(event)
    db.commit()
    return None


# =====================================================
# Market Risk Exposure Endpoints
# =====================================================

@router.post("/market-exposures", response_model=MarketRiskExposureResponse, status_code=201)
def create_market_risk_exposure(
    exposure: MarketRiskExposureCreate,
    db: Session = Depends(get_db)
):
    """Create a new market risk exposure record"""
    db_exposure = MarketRiskExposure(**exposure.model_dump())
    db.add(db_exposure)
    db.commit()
    db.refresh(db_exposure)
    return db_exposure


@router.get("/market-exposures", response_model=List[MarketRiskExposureResponse])
def list_market_risk_exposures(
    exposure_type: Optional[str] = None,
    currency: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List market risk exposures with filters"""
    query = db.query(MarketRiskExposure)
    
    if exposure_type:
        query = query.filter(MarketRiskExposure.exposure_type == exposure_type)
    if currency:
        query = query.filter(MarketRiskExposure.currency == currency)
    if date_from:
        query = query.filter(MarketRiskExposure.exposure_date >= date_from)
    if date_to:
        query = query.filter(MarketRiskExposure.exposure_date <= date_to)
    
    query = query.order_by(desc(MarketRiskExposure.exposure_date))
    return query.offset(skip).limit(limit).all()


@router.get("/market-exposures/{exposure_id}", response_model=MarketRiskExposureResponse)
def get_market_risk_exposure(exposure_id: UUID, db: Session = Depends(get_db)):
    """Get market risk exposure by ID"""
    exposure = db.query(MarketRiskExposure).filter(
        MarketRiskExposure.exposure_id == exposure_id
    ).first()
    if not exposure:
        raise HTTPException(status_code=404, detail="Market risk exposure not found")
    return exposure


@router.delete("/market-exposures/{exposure_id}", status_code=204)
def delete_market_risk_exposure(exposure_id: UUID, db: Session = Depends(get_db)):
    """Delete market risk exposure"""
    exposure = db.query(MarketRiskExposure).filter(
        MarketRiskExposure.exposure_id == exposure_id
    ).first()
    if not exposure:
        raise HTTPException(status_code=404, detail="Market risk exposure not found")
    
    db.delete(exposure)
    db.commit()
    return None


# =====================================================
# Concentration Risk Limit Endpoints
# =====================================================

@router.post("/concentration-limits", response_model=ConcentrationRiskLimitResponse, status_code=201)
def create_concentration_risk_limit(
    limit: ConcentrationRiskLimitCreate,
    db: Session = Depends(get_db)
):
    """Create a new concentration risk limit"""
    db_limit = ConcentrationRiskLimit(**limit.model_dump())
    db.add(db_limit)
    db.commit()
    db.refresh(db_limit)
    return db_limit


@router.get("/concentration-limits", response_model=List[ConcentrationRiskLimitResponse])
def list_concentration_risk_limits(
    concentration_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List concentration risk limits with filters"""
    query = db.query(ConcentrationRiskLimit)
    
    if concentration_type:
        query = query.filter(ConcentrationRiskLimit.concentration_type == concentration_type)
    if is_active is not None:
        query = query.filter(ConcentrationRiskLimit.is_active == is_active)
    
    query = query.order_by(ConcentrationRiskLimit.limit_name)
    return query.offset(skip).limit(limit).all()


@router.get("/concentration-limits/{limit_id}", response_model=ConcentrationRiskLimitResponse)
def get_concentration_risk_limit(limit_id: UUID, db: Session = Depends(get_db)):
    """Get concentration risk limit by ID"""
    limit = db.query(ConcentrationRiskLimit).filter(
        ConcentrationRiskLimit.limit_id == limit_id
    ).first()
    if not limit:
        raise HTTPException(status_code=404, detail="Concentration risk limit not found")
    return limit


@router.put("/concentration-limits/{limit_id}", response_model=ConcentrationRiskLimitResponse)
def update_concentration_risk_limit(
    limit_id: UUID,
    limit: ConcentrationRiskLimitUpdate,
    db: Session = Depends(get_db)
):
    """Update concentration risk limit"""
    db_limit = db.query(ConcentrationRiskLimit).filter(
        ConcentrationRiskLimit.limit_id == limit_id
    ).first()
    if not db_limit:
        raise HTTPException(status_code=404, detail="Concentration risk limit not found")
    
    update_data = limit.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_limit, field, value)
    
    db.commit()
    db.refresh(db_limit)
    return db_limit


@router.get("/concentration-limits/monitor", response_model=List[ConcentrationRiskMonitorResponse])
def monitor_concentration_risks(
    db: Session = Depends(get_db)
):
    """Monitor concentration risk utilization against limits"""
    limits = db.query(ConcentrationRiskLimit).filter(
        ConcentrationRiskLimit.is_active == True
    ).all()
    
    monitoring_results = []
    for limit in limits:
        # In production, calculate actual exposure based on limit type
        # This is a placeholder calculation
        utilization_percentage = (limit.current_utilization / limit.limit_amount * 100) if limit.limit_amount else 0
        
        breach_status = 'within_limit'
        if utilization_percentage >= 100:
            breach_status = 'breached'
        elif utilization_percentage >= limit.warning_threshold:
            breach_status = 'warning'
        
        monitoring_results.append(ConcentrationRiskMonitorResponse(
            limit_id=limit.limit_id,
            limit_name=limit.limit_name,
            concentration_type=limit.concentration_type,
            limit_amount=limit.limit_amount,
            current_utilization=limit.current_utilization,
            utilization_percentage=utilization_percentage,
            breach_status=breach_status
        ))
    
    return monitoring_results


@router.delete("/concentration-limits/{limit_id}", status_code=204)
def delete_concentration_risk_limit(limit_id: UUID, db: Session = Depends(get_db)):
    """Delete concentration risk limit"""
    limit = db.query(ConcentrationRiskLimit).filter(
        ConcentrationRiskLimit.limit_id == limit_id
    ).first()
    if not limit:
        raise HTTPException(status_code=404, detail="Concentration risk limit not found")
    
    db.delete(limit)
    db.commit()
    return None


# =====================================================
# Risk Alert Endpoints
# =====================================================

@router.post("/alerts", response_model=RiskAlertResponse, status_code=201)
def create_risk_alert(
    alert: RiskAlertCreate,
    db: Session = Depends(get_db)
):
    """Create a new risk alert"""
    db_alert = RiskAlert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/alerts", response_model=List[RiskAlertResponse])
def list_risk_alerts(
    alert_type: Optional[str] = None,
    risk_category: Optional[str] = None,
    severity_level: Optional[str] = None,
    alert_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List risk alerts with filters"""
    query = db.query(RiskAlert)
    
    if alert_type:
        query = query.filter(RiskAlert.alert_type == alert_type)
    if risk_category:
        query = query.filter(RiskAlert.risk_category == risk_category)
    if severity_level:
        query = query.filter(RiskAlert.severity_level == severity_level)
    if alert_status:
        query = query.filter(RiskAlert.alert_status == alert_status)
    if date_from:
        query = query.filter(RiskAlert.alert_date >= date_from)
    if date_to:
        query = query.filter(RiskAlert.alert_date <= date_to)
    
    query = query.order_by(desc(RiskAlert.alert_date))
    return query.offset(skip).limit(limit).all()


@router.get("/alerts/{alert_id}", response_model=RiskAlertResponse)
def get_risk_alert(alert_id: UUID, db: Session = Depends(get_db)):
    """Get risk alert by ID"""
    alert = db.query(RiskAlert).filter(
        RiskAlert.alert_id == alert_id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")
    return alert


@router.put("/alerts/{alert_id}", response_model=RiskAlertResponse)
def update_risk_alert(
    alert_id: UUID,
    alert: RiskAlertUpdate,
    db: Session = Depends(get_db)
):
    """Update risk alert"""
    db_alert = db.query(RiskAlert).filter(
        RiskAlert.alert_id == alert_id
    ).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")
    
    update_data = alert.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.post("/alerts/{alert_id}/resolve", response_model=RiskAlertResponse)
def resolve_risk_alert(
    alert_id: UUID,
    request: RiskAlertResolveRequest,
    db: Session = Depends(get_db)
):
    """Resolve a risk alert"""
    alert = db.query(RiskAlert).filter(
        RiskAlert.alert_id == alert_id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")
    
    if alert.alert_status == 'resolved':
        raise HTTPException(status_code=400, detail="Alert already resolved")
    
    alert.alert_status = 'resolved'
    alert.resolved_by = request.resolved_by
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = request.resolution_notes
    
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/alerts/{alert_id}", status_code=204)
def delete_risk_alert(alert_id: UUID, db: Session = Depends(get_db)):
    """Delete risk alert"""
    alert = db.query(RiskAlert).filter(
        RiskAlert.alert_id == alert_id
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Risk alert not found")
    
    db.delete(alert)
    db.commit()
    return None


# =====================================================
# Risk Mitigation Endpoints
# =====================================================

@router.post("/mitigations", response_model=RiskMitigationResponse, status_code=201)
def create_risk_mitigation(
    mitigation: RiskMitigationCreate,
    db: Session = Depends(get_db)
):
    """Create a new risk mitigation plan"""
    db_mitigation = RiskMitigation(**mitigation.model_dump())
    db.add(db_mitigation)
    db.commit()
    db.refresh(db_mitigation)
    return db_mitigation


@router.get("/mitigations", response_model=List[RiskMitigationResponse])
def list_risk_mitigations(
    risk_category: Optional[str] = None,
    mitigation_type: Optional[str] = None,
    mitigation_status: Optional[str] = None,
    approval_status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List risk mitigations with filters"""
    query = db.query(RiskMitigation)
    
    if risk_category:
        query = query.filter(RiskMitigation.risk_category == risk_category)
    if mitigation_type:
        query = query.filter(RiskMitigation.mitigation_type == mitigation_type)
    if mitigation_status:
        query = query.filter(RiskMitigation.mitigation_status == mitigation_status)
    if approval_status:
        query = query.filter(RiskMitigation.approval_status == approval_status)
    
    query = query.order_by(desc(RiskMitigation.created_at))
    return query.offset(skip).limit(limit).all()


@router.get("/mitigations/{mitigation_id}", response_model=RiskMitigationResponse)
def get_risk_mitigation(mitigation_id: UUID, db: Session = Depends(get_db)):
    """Get risk mitigation by ID"""
    mitigation = db.query(RiskMitigation).filter(
        RiskMitigation.mitigation_id == mitigation_id
    ).first()
    if not mitigation:
        raise HTTPException(status_code=404, detail="Risk mitigation not found")
    return mitigation


@router.put("/mitigations/{mitigation_id}", response_model=RiskMitigationResponse)
def update_risk_mitigation(
    mitigation_id: UUID,
    mitigation: RiskMitigationUpdate,
    db: Session = Depends(get_db)
):
    """Update risk mitigation"""
    db_mitigation = db.query(RiskMitigation).filter(
        RiskMitigation.mitigation_id == mitigation_id
    ).first()
    if not db_mitigation:
        raise HTTPException(status_code=404, detail="Risk mitigation not found")
    
    if db_mitigation.approval_status == 'approved':
        raise HTTPException(status_code=400, detail="Cannot update approved mitigation")
    
    update_data = mitigation.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mitigation, field, value)
    
    db.commit()
    db.refresh(db_mitigation)
    return db_mitigation


@router.post("/mitigations/{mitigation_id}/approve", response_model=RiskMitigationResponse)
def approve_risk_mitigation(
    mitigation_id: UUID,
    request: RiskMitigationApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve risk mitigation plan"""
    mitigation = db.query(RiskMitigation).filter(
        RiskMitigation.mitigation_id == mitigation_id
    ).first()
    if not mitigation:
        raise HTTPException(status_code=404, detail="Risk mitigation not found")
    
    if mitigation.approval_status == 'approved':
        raise HTTPException(status_code=400, detail="Mitigation already approved")
    
    mitigation.approval_status = 'approved'
    mitigation.approved_by = request.approved_by
    mitigation.approved_at = datetime.utcnow()
    mitigation.approval_notes = request.approval_notes
    
    db.commit()
    db.refresh(mitigation)
    return mitigation


@router.delete("/mitigations/{mitigation_id}", status_code=204)
def delete_risk_mitigation(mitigation_id: UUID, db: Session = Depends(get_db)):
    """Delete risk mitigation"""
    mitigation = db.query(RiskMitigation).filter(
        RiskMitigation.mitigation_id == mitigation_id
    ).first()
    if not mitigation:
        raise HTTPException(status_code=404, detail="Risk mitigation not found")
    
    if mitigation.approval_status == 'approved':
        raise HTTPException(status_code=403, detail="Cannot delete approved mitigation")
    
    db.delete(mitigation)
    db.commit()
    return None


# =====================================================
# Risk Report Endpoints
# =====================================================

@router.post("/reports", response_model=RiskReportResponse, status_code=201)
def create_risk_report(
    report: RiskReportCreate,
    db: Session = Depends(get_db)
):
    """Create a new risk report"""
    db_report = RiskReport(**report.model_dump())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


@router.get("/reports", response_model=List[RiskReportResponse])
def list_risk_reports(
    report_type: Optional[str] = None,
    report_category: Optional[str] = None,
    report_status: Optional[str] = None,
    approval_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List risk reports with filters"""
    query = db.query(RiskReport)
    
    if report_type:
        query = query.filter(RiskReport.report_type == report_type)
    if report_category:
        query = query.filter(RiskReport.report_category == report_category)
    if report_status:
        query = query.filter(RiskReport.report_status == report_status)
    if approval_status:
        query = query.filter(RiskReport.approval_status == approval_status)
    if date_from:
        query = query.filter(RiskReport.report_period_from >= date_from)
    if date_to:
        query = query.filter(RiskReport.report_period_to <= date_to)
    
    query = query.order_by(desc(RiskReport.created_at))
    return query.offset(skip).limit(limit).all()


@router.get("/reports/{report_id}", response_model=RiskReportResponse)
def get_risk_report(report_id: UUID, db: Session = Depends(get_db)):
    """Get risk report by ID"""
    report = db.query(RiskReport).filter(
        RiskReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Risk report not found")
    return report


@router.put("/reports/{report_id}", response_model=RiskReportResponse)
def update_risk_report(
    report_id: UUID,
    report: RiskReportUpdate,
    db: Session = Depends(get_db)
):
    """Update risk report"""
    db_report = db.query(RiskReport).filter(
        RiskReport.report_id == report_id
    ).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="Risk report not found")
    
    if db_report.approval_status == 'approved':
        raise HTTPException(status_code=400, detail="Cannot update approved report")
    
    update_data = report.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)
    
    db.commit()
    db.refresh(db_report)
    return db_report


@router.post("/reports/{report_id}/approve", response_model=RiskReportResponse)
def approve_risk_report(
    report_id: UUID,
    request: RiskReportApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve risk report"""
    report = db.query(RiskReport).filter(
        RiskReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Risk report not found")
    
    if report.approval_status == 'approved':
        raise HTTPException(status_code=400, detail="Report already approved")
    
    report.approval_status = 'approved'
    report.approved_by = request.approved_by
    report.approved_at = datetime.utcnow()
    report.approval_notes = request.approval_notes
    
    db.commit()
    db.refresh(report)
    return report


@router.post("/reports/{report_id}/publish", response_model=RiskReportResponse)
def publish_risk_report(
    report_id: UUID,
    request: RiskReportPublishRequest,
    db: Session = Depends(get_db)
):
    """Publish risk report"""
    report = db.query(RiskReport).filter(
        RiskReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Risk report not found")
    
    if report.approval_status != 'approved':
        raise HTTPException(status_code=400, detail="Report must be approved before publishing")
    
    if report.report_status == 'published':
        raise HTTPException(status_code=400, detail="Report already published")
    
    report.report_status = 'published'
    report.published_by = request.published_by
    report.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    return report


@router.delete("/reports/{report_id}", status_code=204)
def delete_risk_report(report_id: UUID, db: Session = Depends(get_db)):
    """Delete risk report"""
    report = db.query(RiskReport).filter(
        RiskReport.report_id == report_id
    ).first()
    if not report:
        raise HTTPException(status_code=404, detail="Risk report not found")
    
    if report.approval_status == 'approved':
        raise HTTPException(status_code=403, detail="Cannot delete approved report")
    
    db.delete(report)
    db.commit()
    return None


# =====================================================
# Risk Dashboard Endpoints
# =====================================================

@router.post("/dashboards", response_model=RiskDashboardResponse, status_code=201)
def create_risk_dashboard(
    dashboard: RiskDashboardCreate,
    db: Session = Depends(get_db)
):
    """Create a new risk dashboard"""
    # Check for duplicate code
    existing = db.query(RiskDashboard).filter(
        RiskDashboard.dashboard_code == dashboard.dashboard_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dashboard code already exists")
    
    db_dashboard = RiskDashboard(**dashboard.model_dump())
    db.add(db_dashboard)
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.get("/dashboards", response_model=List[RiskDashboardResponse])
def list_risk_dashboards(
    dashboard_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List risk dashboards with filters"""
    query = db.query(RiskDashboard)
    
    if dashboard_type:
        query = query.filter(RiskDashboard.dashboard_type == dashboard_type)
    if is_active is not None:
        query = query.filter(RiskDashboard.is_active == is_active)
    
    query = query.order_by(RiskDashboard.dashboard_name)
    return query.offset(skip).limit(limit).all()


@router.get("/dashboards/{dashboard_id}", response_model=RiskDashboardResponse)
def get_risk_dashboard(dashboard_id: UUID, db: Session = Depends(get_db)):
    """Get risk dashboard by ID"""
    dashboard = db.query(RiskDashboard).filter(
        RiskDashboard.dashboard_id == dashboard_id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Risk dashboard not found")
    return dashboard


@router.put("/dashboards/{dashboard_id}", response_model=RiskDashboardResponse)
def update_risk_dashboard(
    dashboard_id: UUID,
    dashboard: RiskDashboardUpdate,
    db: Session = Depends(get_db)
):
    """Update risk dashboard"""
    db_dashboard = db.query(RiskDashboard).filter(
        RiskDashboard.dashboard_id == dashboard_id
    ).first()
    if not db_dashboard:
        raise HTTPException(status_code=404, detail="Risk dashboard not found")
    
    update_data = dashboard.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_dashboard, field, value)
    
    db.commit()
    db.refresh(db_dashboard)
    return db_dashboard


@router.delete("/dashboards/{dashboard_id}", status_code=204)
def delete_risk_dashboard(dashboard_id: UUID, db: Session = Depends(get_db)):
    """Delete risk dashboard"""
    dashboard = db.query(RiskDashboard).filter(
        RiskDashboard.dashboard_id == dashboard_id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Risk dashboard not found")
    
    db.delete(dashboard)
    db.commit()
    return None


# =====================================================
# Compliance Check Endpoints
# =====================================================

@router.post("/compliance-checks", response_model=ComplianceCheckResponse, status_code=201)
def create_compliance_check(
    check: ComplianceCheckCreate,
    db: Session = Depends(get_db)
):
    """Create a new compliance check"""
    db_check = ComplianceCheck(**check.model_dump())
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check


@router.get("/compliance-checks", response_model=List[ComplianceCheckResponse])
def list_compliance_checks(
    check_type: Optional[str] = None,
    compliance_area: Optional[str] = None,
    check_status: Optional[str] = None,
    compliance_status: Optional[str] = None,
    review_status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List compliance checks with filters"""
    query = db.query(ComplianceCheck)
    
    if check_type:
        query = query.filter(ComplianceCheck.check_type == check_type)
    if compliance_area:
        query = query.filter(ComplianceCheck.compliance_area == compliance_area)
    if check_status:
        query = query.filter(ComplianceCheck.check_status == check_status)
    if compliance_status:
        query = query.filter(ComplianceCheck.compliance_status == compliance_status)
    if review_status:
        query = query.filter(ComplianceCheck.review_status == review_status)
    if date_from:
        query = query.filter(ComplianceCheck.check_date >= date_from)
    if date_to:
        query = query.filter(ComplianceCheck.check_date <= date_to)
    
    query = query.order_by(desc(ComplianceCheck.check_date))
    return query.offset(skip).limit(limit).all()


@router.get("/compliance-checks/{check_id}", response_model=ComplianceCheckResponse)
def get_compliance_check(check_id: UUID, db: Session = Depends(get_db)):
    """Get compliance check by ID"""
    check = db.query(ComplianceCheck).filter(
        ComplianceCheck.check_id == check_id
    ).first()
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    return check


@router.put("/compliance-checks/{check_id}", response_model=ComplianceCheckResponse)
def update_compliance_check(
    check_id: UUID,
    check: ComplianceCheckUpdate,
    db: Session = Depends(get_db)
):
    """Update compliance check"""
    db_check = db.query(ComplianceCheck).filter(
        ComplianceCheck.check_id == check_id
    ).first()
    if not db_check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    
    if db_check.review_status == 'approved':
        raise HTTPException(status_code=400, detail="Cannot update approved compliance check")
    
    update_data = check.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_check, field, value)
    
    db.commit()
    db.refresh(db_check)
    return db_check


@router.post("/compliance-checks/{check_id}/review", response_model=ComplianceCheckResponse)
def review_compliance_check(
    check_id: UUID,
    request: ComplianceCheckReviewRequest,
    db: Session = Depends(get_db)
):
    """Review compliance check"""
    check = db.query(ComplianceCheck).filter(
        ComplianceCheck.check_id == check_id
    ).first()
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    
    if check.review_status in ['reviewed', 'approved']:
        raise HTTPException(status_code=400, detail="Compliance check already reviewed")
    
    check.review_status = 'reviewed'
    check.reviewed_by = request.reviewed_by
    check.reviewed_at = datetime.utcnow()
    check.review_notes = request.review_notes
    
    db.commit()
    db.refresh(check)
    return check


@router.post("/compliance-checks/{check_id}/approve", response_model=ComplianceCheckResponse)
def approve_compliance_check(
    check_id: UUID,
    request: ComplianceCheckApprovalRequest,
    db: Session = Depends(get_db)
):
    """Approve compliance check"""
    check = db.query(ComplianceCheck).filter(
        ComplianceCheck.check_id == check_id
    ).first()
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    
    if check.review_status == 'approved':
        raise HTTPException(status_code=400, detail="Compliance check already approved")
    
    check.review_status = 'approved'
    check.approved_by = request.approved_by
    check.approved_at = datetime.utcnow()
    check.approval_notes = request.approval_notes
    
    db.commit()
    db.refresh(check)
    return check


@router.delete("/compliance-checks/{check_id}", status_code=204)
def delete_compliance_check(check_id: UUID, db: Session = Depends(get_db)):
    """Delete compliance check"""
    check = db.query(ComplianceCheck).filter(
        ComplianceCheck.check_id == check_id
    ).first()
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    
    if check.review_status == 'approved':
        raise HTTPException(status_code=403, detail="Cannot delete approved compliance check")
    
    db.delete(check)
    db.commit()
    return None


# =====================================================
# Statistics Endpoints
# =====================================================

@router.get("/statistics/credit-risk", response_model=CreditRiskStatistics)
def get_credit_risk_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get credit risk statistics"""
    query = db.query(CreditRiskAssessment)
    
    if date_from:
        query = query.filter(CreditRiskAssessment.assessment_date >= date_from)
    if date_to:
        query = query.filter(CreditRiskAssessment.assessment_date <= date_to)
    
    assessments = query.all()
    
    total_assessments = len(assessments)
    by_risk_category = {}
    by_approval_status = {}
    total_provision = sum(a.provision_amount or 0 for a in assessments)
    avg_risk_score = sum(a.overall_risk_score for a in assessments) / total_assessments if total_assessments > 0 else 0
    
    for assessment in assessments:
        by_risk_category[assessment.risk_category] = by_risk_category.get(assessment.risk_category, 0) + 1
        by_approval_status[assessment.approval_status] = by_approval_status.get(assessment.approval_status, 0) + 1
    
    return CreditRiskStatistics(
        total_assessments=total_assessments,
        assessments_by_risk_category=by_risk_category,
        assessments_by_approval_status=by_approval_status,
        total_provision_amount=total_provision,
        average_risk_score=avg_risk_score
    )


@router.get("/statistics/operational-risk", response_model=OperationalRiskStatistics)
def get_operational_risk_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get operational risk statistics"""
    query = db.query(OperationalRiskEvent)
    
    if date_from:
        query = query.filter(OperationalRiskEvent.event_date >= date_from)
    if date_to:
        query = query.filter(OperationalRiskEvent.event_date <= date_to)
    
    events = query.all()
    
    total_events = len(events)
    by_category = {}
    by_severity = {}
    by_status = {}
    total_loss = sum(e.actual_loss_amount or 0 for e in events)
    
    for event in events:
        by_category[event.event_category] = by_category.get(event.event_category, 0) + 1
        by_severity[event.severity_level] = by_severity.get(event.severity_level, 0) + 1
        by_status[event.event_status] = by_status.get(event.event_status, 0) + 1
    
    return OperationalRiskStatistics(
        total_events=total_events,
        events_by_category=by_category,
        events_by_severity=by_severity,
        events_by_status=by_status,
        total_loss_amount=total_loss
    )


@router.get("/statistics/market-risk", response_model=MarketRiskStatistics)
def get_market_risk_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get market risk statistics"""
    query = db.query(MarketRiskExposure)
    
    if date_from:
        query = query.filter(MarketRiskExposure.exposure_date >= date_from)
    if date_to:
        query = query.filter(MarketRiskExposure.exposure_date <= date_to)
    
    exposures = query.all()
    
    total_exposures = len(exposures)
    by_type = {}
    by_currency = {}
    total_exposure = sum(e.exposure_amount or 0 for e in exposures)
    total_var = sum(e.var_amount or 0 for e in exposures)
    
    for exposure in exposures:
        by_type[exposure.exposure_type] = by_type.get(exposure.exposure_type, 0) + 1
        if exposure.currency:
            by_currency[exposure.currency] = by_currency.get(exposure.currency, 0) + 1
    
    return MarketRiskStatistics(
        total_exposures=total_exposures,
        exposures_by_type=by_type,
        exposures_by_currency=by_currency,
        total_exposure_amount=total_exposure,
        total_var_amount=total_var
    )


@router.get("/statistics/concentration-risk", response_model=ConcentrationRiskStatistics)
def get_concentration_risk_statistics(
    db: Session = Depends(get_db)
):
    """Get concentration risk statistics"""
    limits = db.query(ConcentrationRiskLimit).filter(
        ConcentrationRiskLimit.is_active == True
    ).all()
    
    total_limits = len(limits)
    by_type = {}
    breached_limits = 0
    warning_limits = 0
    total_limit_amount = sum(l.limit_amount or 0 for l in limits)
    total_utilization = sum(l.current_utilization or 0 for l in limits)
    
    for limit in limits:
        by_type[limit.concentration_type] = by_type.get(limit.concentration_type, 0) + 1
        
        utilization_pct = (limit.current_utilization / limit.limit_amount * 100) if limit.limit_amount else 0
        if utilization_pct >= 100:
            breached_limits += 1
        elif utilization_pct >= limit.warning_threshold:
            warning_limits += 1
    
    return ConcentrationRiskStatistics(
        total_limits=total_limits,
        limits_by_type=by_type,
        breached_limits=breached_limits,
        warning_limits=warning_limits,
        total_limit_amount=total_limit_amount,
        total_utilization=total_utilization
    )


@router.get("/statistics/compliance", response_model=ComplianceStatistics)
def get_compliance_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Get compliance statistics"""
    query = db.query(ComplianceCheck)
    
    if date_from:
        query = query.filter(ComplianceCheck.check_date >= date_from)
    if date_to:
        query = query.filter(ComplianceCheck.check_date <= date_to)
    
    checks = query.all()
    
    total_checks = len(checks)
    by_area = {}
    by_status = {}
    by_compliance_status = {}
    by_review_status = {}
    
    for check in checks:
        by_area[check.compliance_area] = by_area.get(check.compliance_area, 0) + 1
        by_status[check.check_status] = by_status.get(check.check_status, 0) + 1
        by_compliance_status[check.compliance_status] = by_compliance_status.get(check.compliance_status, 0) + 1
        by_review_status[check.review_status] = by_review_status.get(check.review_status, 0) + 1
    
    return ComplianceStatistics(
        total_checks=total_checks,
        checks_by_area=by_area,
        checks_by_status=by_status,
        checks_by_compliance_status=by_compliance_status,
        checks_by_review_status=by_review_status
    )
