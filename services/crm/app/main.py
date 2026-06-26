from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, Column, String, DateTime, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Lead(Base):
    __tablename__ = "crm_leads"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    customer_id = Column(String, nullable=True)
    source = Column(String)
    status = Column(String, default="new")
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column("metadata", JSON, nullable=True)


class Campaign(Base):
    __tablename__ = "crm_campaigns"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    name = Column(String)
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    status = Column(String, default="planned")
    created_at = Column(DateTime, default=datetime.utcnow)


class Opportunity(Base):
    __tablename__ = "crm_opportunities"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    lead_id = Column(String)
    product_code = Column(String)
    stage = Column(String, default="prospecting")
    value = Column(Float)
    probability = Column(Float)
    close_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CRMReportDefinition(Base):
    __tablename__ = "crm_report_definitions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    data_source = Column(String, nullable=False)
    columns = Column(JSON, nullable=False)
    filters = Column(JSON, nullable=True)
    group_by = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CRMDashboardDefinition(Base):
    __tablename__ = "crm_dashboards"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    widgets = Column(JSON, nullable=False)
    is_default = Column(String, default="false")
    created_at = Column(DateTime, default=datetime.utcnow)


class LeadCreate(BaseModel):
    tenant_id: str
    source: str
    assigned_to: Optional[str] = None
    metadata: Optional[dict] = None


class LeadResponse(BaseModel):
    id: str
    tenant_id: str
    source: str
    status: str
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None

    class Config:
        from_attributes = True


class CampaignCreate(BaseModel):
    tenant_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    budget: float


class CampaignResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    budget: float
    status: str

    class Config:
        from_attributes = True


class OpportunityCreate(BaseModel):
    tenant_id: str
    lead_id: str
    product_code: str
    value: float
    probability: float
    close_date: Optional[datetime] = None


class OpportunityResponse(BaseModel):
    id: str
    tenant_id: str
    lead_id: str
    product_code: str
    stage: str
    value: float
    probability: float
    close_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class CRMReportDefinitionCreate(BaseModel):
    tenant_id: str
    name: str
    data_source: str
    columns: List[str] = Field(default_factory=list)
    filters: dict = Field(default_factory=dict)
    group_by: List[str] = Field(default_factory=list)


class CRMReportDefinitionResponse(CRMReportDefinitionCreate):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class CRMReportExecuteRequest(BaseModel):
    tenant_id: str
    data_source: Optional[str] = None
    columns: Optional[List[str]] = None
    filters: dict = Field(default_factory=dict)
    group_by: List[str] = Field(default_factory=list)


class DashboardWidget(BaseModel):
    widget_id: str
    title: str
    data_source: str
    metric: str
    filters: dict = Field(default_factory=dict)


class CRMDashboardCreate(BaseModel):
    tenant_id: str
    name: str
    widgets: List[DashboardWidget]
    is_default: bool = False


class CRMDashboardResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    widgets: list
    is_default: str
    created_at: datetime

    class Config:
        from_attributes = True


ALLOWED_REPORT_COLUMNS = {
    "leads": {"id", "tenant_id", "source", "status", "assigned_to", "created_at", "updated_at"},
    "opportunities": {"id", "tenant_id", "lead_id", "product_code", "stage", "value", "probability", "close_date", "created_at", "updated_at"},
    "campaigns": {"id", "tenant_id", "name", "description", "start_date", "end_date", "budget", "status", "created_at"},
}

REPORT_MODELS = {
    "leads": Lead,
    "opportunities": Opportunity,
    "campaigns": Campaign,
}


app = FastAPI(title="crm-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _lead_response(lead: Lead) -> dict:
    return {
        "id": lead.id,
        "tenant_id": lead.tenant_id,
        "source": lead.source,
        "status": lead.status,
        "assigned_to": lead.assigned_to,
        "created_at": lead.created_at,
        "updated_at": lead.updated_at,
        "metadata": lead.metadata_json,
    }


def _opportunity_response(opportunity: Opportunity) -> dict:
    return {
        "id": opportunity.id,
        "tenant_id": opportunity.tenant_id,
        "lead_id": opportunity.lead_id,
        "product_code": opportunity.product_code,
        "stage": opportunity.stage,
        "value": opportunity.value,
        "probability": opportunity.probability,
        "close_date": opportunity.close_date,
    }


def _validate_report(data_source: str, columns: list[str], filters: dict, group_by: list[str]):
    if data_source not in REPORT_MODELS:
        raise HTTPException(status_code=400, detail="Unsupported CRM data source")
    allowed = ALLOWED_REPORT_COLUMNS[data_source]
    requested_columns = columns or list(allowed)
    invalid_columns = set(requested_columns) - allowed
    invalid_filters = set(filters) - allowed
    invalid_groups = set(group_by) - allowed
    if invalid_columns:
        raise HTTPException(status_code=400, detail=f"Unsupported columns: {sorted(invalid_columns)}")
    if invalid_filters:
        raise HTTPException(status_code=400, detail=f"Unsupported filters: {sorted(invalid_filters)}")
    if invalid_groups:
        raise HTTPException(status_code=400, detail=f"Unsupported group_by: {sorted(invalid_groups)}")
    return requested_columns


def _serialize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _row_dict(record, columns: list[str]) -> dict:
    return {column: _serialize_value(getattr(record, column)) for column in columns}


def _apply_filters(query, model, filters: dict):
    for field, expected in filters.items():
        column = getattr(model, field)
        if isinstance(expected, list):
            query = query.filter(column.in_(expected))
        else:
            query = query.filter(column == expected)
    return query


def _execute_report(
    tenant_id: str,
    data_source: str,
    columns: list[str],
    filters: dict,
    group_by: list[str],
    db: Session,
) -> dict:
    selected_columns = _validate_report(data_source, columns, filters, group_by)
    model = REPORT_MODELS[data_source]
    query = db.query(model).filter(model.tenant_id == tenant_id)
    query = _apply_filters(query, model, filters)
    records = query.all()
    rows = [_row_dict(record, selected_columns) for record in records]

    groups = []
    if group_by:
        grouped: dict[tuple, dict] = {}
        for record in records:
            key = tuple(getattr(record, field) for field in group_by)
            if key not in grouped:
                grouped[key] = {
                    "group": {field: _serialize_value(getattr(record, field)) for field in group_by},
                    "count": 0,
                    "value": 0.0,
                    "weighted_value": 0.0,
                }
            grouped[key]["count"] += 1
            if hasattr(record, "value"):
                grouped[key]["value"] += record.value or 0.0
                grouped[key]["weighted_value"] += (record.value or 0.0) * (record.probability or 0.0)
        groups = list(grouped.values())

    return {
        "tenant_id": tenant_id,
        "data_source": data_source,
        "columns": selected_columns,
        "filters": filters,
        "group_by": group_by,
        "row_count": len(rows),
        "rows": rows,
        "groups": groups,
    }


def _pipeline_summary_for_tenant(tenant_id: str, db: Session) -> dict:
    opportunities = db.query(Opportunity).filter(Opportunity.tenant_id == tenant_id).all()
    leads = db.query(Lead).filter(Lead.tenant_id == tenant_id).all()
    by_stage: dict[str, dict[str, float | int]] = {}
    for opportunity in opportunities:
        stage = opportunity.stage or "unknown"
        if stage not in by_stage:
            by_stage[stage] = {"count": 0, "value": 0.0, "weighted_value": 0.0}
        by_stage[stage]["count"] += 1
        by_stage[stage]["value"] += opportunity.value or 0.0
        by_stage[stage]["weighted_value"] += (opportunity.value or 0.0) * (opportunity.probability or 0.0)

    lead_statuses: dict[str, int] = {}
    for lead in leads:
        lead_statuses[lead.status] = lead_statuses.get(lead.status, 0) + 1

    return {
        "tenant_id": tenant_id,
        "opportunity_count": len(opportunities),
        "lead_count": len(leads),
        "by_stage": by_stage,
        "lead_statuses": lead_statuses,
    }


def _render_widget(widget: dict, tenant_id: str, db: Session) -> dict:
    data_source = widget["data_source"]
    metric = widget["metric"]
    filters = widget.get("filters") or {}
    _validate_report(data_source, [], filters, [])
    model = REPORT_MODELS[data_source]
    query = db.query(model).filter(model.tenant_id == tenant_id)
    records = _apply_filters(query, model, filters).all()

    if metric == "count":
        value = len(records)
    elif metric == "sum_value" and data_source == "opportunities":
        value = round(sum(record.value or 0.0 for record in records), 2)
    elif metric == "weighted_value" and data_source == "opportunities":
        value = round(sum((record.value or 0.0) * (record.probability or 0.0) for record in records), 2)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported dashboard metric: {metric}")

    return {
        "widget_id": widget["widget_id"],
        "title": widget["title"],
        "data_source": data_source,
        "metric": metric,
        "value": value,
    }


def _ceo_command_center_widgets() -> list[dict]:
    return [
        {
            "widget_id": "lead-intake",
            "title": "New Leads",
            "data_source": "leads",
            "metric": "count",
            "filters": {"status": "new"},
        },
        {
            "widget_id": "open-pipeline",
            "title": "Open Pipeline",
            "data_source": "opportunities",
            "metric": "sum_value",
            "filters": {"stage": "prospecting"},
        },
        {
            "widget_id": "weighted-pipeline",
            "title": "Weighted Pipeline",
            "data_source": "opportunities",
            "metric": "weighted_value",
            "filters": {"stage": "prospecting"},
        },
    ]


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "crm"}


@app.get("/ready")
async def ready():
    return {"ready": True}


@app.post("/leads", response_model=LeadResponse, status_code=201)
async def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    if not lead.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    new_lead = Lead(
        id=str(uuid4()),
        tenant_id=lead.tenant_id,
        source=lead.source,
        assigned_to=lead.assigned_to,
        metadata_json=lead.metadata,
        status="new"
    )
    db.add(new_lead)
    db.commit()
    db.refresh(new_lead)
    return _lead_response(new_lead)


@app.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(Lead).filter(Lead.tenant_id == tenant_id)
    if status:
        query = query.filter(Lead.status == status)
    if assigned_to:
        query = query.filter(Lead.assigned_to == assigned_to)
    return [_lead_response(lead) for lead in query.offset(skip).limit(limit).all()]


@app.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    if not campaign.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    new_campaign = Campaign(
        id=str(uuid4()),
        tenant_id=campaign.tenant_id,
        name=campaign.name,
        description=campaign.description,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        budget=campaign.budget,
        status="planned"
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign


@app.get("/campaigns", response_model=List[CampaignResponse])
async def list_campaigns(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(Campaign).filter(Campaign.tenant_id == tenant_id)
    if status:
        query = query.filter(Campaign.status == status)
    return query.offset(skip).limit(limit).all()


@app.post("/opportunities", response_model=OpportunityResponse)
async def create_opportunity(opportunity: OpportunityCreate, db: Session = Depends(get_db)):
    if not opportunity.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    lead = (
        db.query(Lead)
        .filter(Lead.id == opportunity.lead_id, Lead.tenant_id == opportunity.tenant_id)
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found for tenant")
    new_opportunity = Opportunity(
        id=str(uuid4()),
        tenant_id=opportunity.tenant_id,
        lead_id=opportunity.lead_id,
        product_code=opportunity.product_code,
        value=opportunity.value,
        probability=opportunity.probability,
        close_date=opportunity.close_date,
        stage="prospecting"
    )
    db.add(new_opportunity)
    db.commit()
    db.refresh(new_opportunity)
    return new_opportunity


@app.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    tenant_id: str = Query(...),
    stage: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity).filter(Opportunity.tenant_id == tenant_id)
    if stage:
        query = query.filter(Opportunity.stage == stage)
    return [_opportunity_response(opportunity) for opportunity in query.offset(skip).limit(limit).all()]


@app.get("/reports/pipeline-summary")
async def pipeline_summary(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _pipeline_summary_for_tenant(tenant_id, db)


@app.post("/leads/{lead_id}/assign")
async def assign_lead(
    lead_id: str,
    assigned_to: str,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found for tenant")
    lead.assigned_to = assigned_to
    lead.status = "contacted"
    db.commit()
    return {"lead_id": lead.id, "assigned_to": lead.assigned_to, "status": lead.status}


@app.post("/leads/{lead_id}/qualify")
async def qualify_lead(
    lead_id: str,
    qualified: bool,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    lead = db.query(Lead).filter(Lead.id == lead_id, Lead.tenant_id == tenant_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found for tenant")
    lead.status = "qualified" if qualified else "disqualified"
    db.commit()
    return {"lead_id": lead.id, "status": lead.status}


@app.post("/reports/definitions", response_model=CRMReportDefinitionResponse)
async def create_report_definition(report: CRMReportDefinitionCreate, db: Session = Depends(get_db)):
    if not report.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    columns = _validate_report(report.data_source, report.columns, report.filters, report.group_by)
    definition = CRMReportDefinition(
        id=str(uuid4()),
        tenant_id=report.tenant_id,
        name=report.name,
        data_source=report.data_source,
        columns=columns,
        filters=report.filters,
        group_by=report.group_by,
    )
    db.add(definition)
    db.commit()
    db.refresh(definition)
    return definition


@app.get("/reports/definitions", response_model=List[CRMReportDefinitionResponse])
async def list_report_definitions(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(CRMReportDefinition).filter(CRMReportDefinition.tenant_id == tenant_id).all()


@app.post("/reports/execute")
async def execute_ad_hoc_report(request: CRMReportExecuteRequest, db: Session = Depends(get_db)):
    if not request.data_source:
        raise HTTPException(status_code=400, detail="data_source is required")
    return _execute_report(
        request.tenant_id,
        request.data_source,
        request.columns or [],
        request.filters,
        request.group_by,
        db,
    )


@app.post("/reports/definitions/{report_id}/execute")
async def execute_saved_report(
    report_id: str,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    definition = (
        db.query(CRMReportDefinition)
        .filter(CRMReportDefinition.id == report_id, CRMReportDefinition.tenant_id == tenant_id)
        .first()
    )
    if not definition:
        raise HTTPException(status_code=404, detail="Report definition not found for tenant")
    return _execute_report(
        tenant_id,
        definition.data_source,
        definition.columns or [],
        definition.filters or {},
        definition.group_by or [],
        db,
    )


@app.post("/dashboards", response_model=CRMDashboardResponse)
async def create_dashboard(dashboard: CRMDashboardCreate, db: Session = Depends(get_db)):
    if not dashboard.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")
    widgets = [widget.model_dump() for widget in dashboard.widgets]
    for widget in widgets:
        _validate_report(widget["data_source"], [], widget.get("filters") or {}, [])
        if widget["metric"] not in {"count", "sum_value", "weighted_value"}:
            raise HTTPException(status_code=400, detail=f"Unsupported dashboard metric: {widget['metric']}")
    definition = CRMDashboardDefinition(
        id=str(uuid4()),
        tenant_id=dashboard.tenant_id,
        name=dashboard.name,
        widgets=widgets,
        is_default="true" if dashboard.is_default else "false",
    )
    db.add(definition)
    db.commit()
    db.refresh(definition)
    return definition


@app.get("/dashboards", response_model=List[CRMDashboardResponse])
async def list_dashboards(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return db.query(CRMDashboardDefinition).filter(CRMDashboardDefinition.tenant_id == tenant_id).all()


@app.get("/dashboards/{dashboard_id}/render")
async def render_dashboard(
    dashboard_id: str,
    tenant_id: str = Query(...),
    db: Session = Depends(get_db),
):
    dashboard = (
        db.query(CRMDashboardDefinition)
        .filter(CRMDashboardDefinition.id == dashboard_id, CRMDashboardDefinition.tenant_id == tenant_id)
        .first()
    )
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found for tenant")
    return {
        "tenant_id": tenant_id,
        "dashboard_id": dashboard.id,
        "name": dashboard.name,
        "widgets": [_render_widget(widget, tenant_id, db) for widget in dashboard.widgets],
    }


@app.post("/dashboards/defaults/ceo-command-center", response_model=CRMDashboardResponse)
async def ensure_ceo_command_center(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    existing = (
        db.query(CRMDashboardDefinition)
        .filter(
            CRMDashboardDefinition.tenant_id == tenant_id,
            CRMDashboardDefinition.name == "CEO Command Center",
        )
        .first()
    )
    if existing:
        return existing
    dashboard = CRMDashboardDefinition(
        id=str(uuid4()),
        tenant_id=tenant_id,
        name="CEO Command Center",
        widgets=_ceo_command_center_widgets(),
        is_default="true",
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard


@app.get("/dashboards/defaults/ceo-command-center/render")
async def render_ceo_command_center(tenant_id: str = Query(...), db: Session = Depends(get_db)):
    dashboard = await ensure_ceo_command_center(tenant_id, db)
    return {
        "tenant_id": tenant_id,
        "dashboard_id": dashboard.id,
        "name": dashboard.name,
        "pipeline_summary": _pipeline_summary_for_tenant(tenant_id, db),
        "widgets": [_render_widget(widget, tenant_id, db) for widget in dashboard.widgets],
    }


@app.get("/")
async def root():
    return {"service": "crm", "version": "0.1.0"}
