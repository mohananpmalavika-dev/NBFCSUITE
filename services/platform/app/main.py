from datetime import datetime
from typing import Any, List, Optional
from uuid import uuid4
import os

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import Column, DateTime, Integer, JSON, String, UniqueConstraint, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://nbfc_user:nbfc_pass@localhost:5432/nbfcsuite")
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ProductDefinition(Base):
    __tablename__ = "platform_product_definitions"
    __table_args__ = (UniqueConstraint("tenant_id", "product_code", "version", name="uq_platform_product_tenant_code_version"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    product_code = Column(String, index=True, nullable=False)
    product_name = Column(String, nullable=False)
    product_family = Column(String, index=True, nullable=False)
    version = Column(Integer, default=1)
    status = Column(String, default="draft", index=True)
    parameters = Column(JSON, nullable=True)
    eligibility_rules = Column(JSON, nullable=True)
    pricing_rules = Column(JSON, nullable=True)
    fee_rules = Column(JSON, nullable=True)
    lifecycle_workflow_code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RuleSet(Base):
    __tablename__ = "platform_rule_sets"
    __table_args__ = (UniqueConstraint("tenant_id", "rule_set_code", "version", name="uq_platform_rule_set_tenant_code_version"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    rule_set_code = Column(String, index=True, nullable=False)
    rule_set_name = Column(String, nullable=False)
    version = Column(Integer, default=1)
    status = Column(String, default="active", index=True)
    rules = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowDefinition(Base):
    __tablename__ = "platform_workflow_definitions"
    __table_args__ = (UniqueConstraint("tenant_id", "workflow_code", "version", name="uq_platform_workflow_tenant_code_version"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    workflow_code = Column(String, index=True, nullable=False)
    workflow_name = Column(String, nullable=False)
    version = Column(Integer, default=1)
    status = Column(String, default="active", index=True)
    initial_state = Column(String, nullable=False)
    terminal_states = Column(JSON, nullable=True)
    transitions = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkflowInstance(Base):
    __tablename__ = "platform_workflow_instances"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    workflow_definition_id = Column(String, index=True, nullable=False)
    workflow_code = Column(String, index=True, nullable=False)
    subject_type = Column(String, index=True, nullable=False)
    subject_id = Column(String, index=True, nullable=False)
    business_key = Column(String, index=True, nullable=True)
    current_state = Column(String, index=True, nullable=False)
    status = Column(String, default="running", index=True)
    context = Column(JSON, nullable=True)
    history = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class DomainEvent(Base):
    __tablename__ = "platform_domain_events"
    __table_args__ = (UniqueConstraint("tenant_id", "idempotency_key", name="uq_platform_event_tenant_idempotency"),)

    id = Column(String, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    source_service = Column(String, index=True, nullable=False)
    aggregate_type = Column(String, index=True, nullable=False)
    aggregate_id = Column(String, index=True, nullable=False)
    payload = Column(JSON, nullable=False)
    idempotency_key = Column(String, nullable=True)
    status = Column(String, default="published", index=True)
    published_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)


class ProductDefinitionCreate(BaseModel):
    tenant_id: str
    product_code: str
    product_name: str
    product_family: str
    version: int = Field(default=1, ge=1)
    status: str = Field(default="draft", pattern="^(draft|active|retired)$")
    parameters: dict = Field(default_factory=dict)
    eligibility_rules: list[dict] = Field(default_factory=list)
    pricing_rules: dict = Field(default_factory=dict)
    fee_rules: dict = Field(default_factory=dict)
    lifecycle_workflow_code: Optional[str] = None


class ProductDefinitionResponse(BaseModel):
    id: str
    tenant_id: str
    product_code: str
    product_name: str
    product_family: str
    version: int
    status: str
    parameters: Optional[dict]
    eligibility_rules: Optional[list]
    pricing_rules: Optional[dict]
    fee_rules: Optional[dict]
    lifecycle_workflow_code: Optional[str]

    class Config:
        from_attributes = True


class RuleSetCreate(BaseModel):
    tenant_id: str
    rule_set_code: str
    rule_set_name: str
    version: int = Field(default=1, ge=1)
    status: str = Field(default="active", pattern="^(active|inactive)$")
    rules: list[dict]


class RuleSetResponse(BaseModel):
    id: str
    tenant_id: str
    rule_set_code: str
    rule_set_name: str
    version: int
    status: str
    rules: list

    class Config:
        from_attributes = True


class RuleEvaluationRequest(BaseModel):
    tenant_id: str
    rule_set_code: Optional[str] = None
    rules: Optional[list[dict]] = None
    context: dict


class ProductSimulationRequest(BaseModel):
    tenant_id: str
    product_code: str
    requested_amount: float = Field(gt=0)
    tenure_months: int = Field(gt=0)
    customer_id: Optional[str] = None
    attributes: dict = Field(default_factory=dict)


class WorkflowDefinitionCreate(BaseModel):
    tenant_id: str
    workflow_code: str
    workflow_name: str
    version: int = Field(default=1, ge=1)
    status: str = Field(default="active", pattern="^(active|inactive)$")
    initial_state: str
    terminal_states: list[str] = Field(default_factory=list)
    transitions: list[dict]


class WorkflowDefinitionResponse(BaseModel):
    id: str
    tenant_id: str
    workflow_code: str
    workflow_name: str
    version: int
    status: str
    initial_state: str
    terminal_states: Optional[list]
    transitions: list

    class Config:
        from_attributes = True


class WorkflowStartRequest(BaseModel):
    tenant_id: str
    workflow_code: str
    subject_type: str
    subject_id: str
    business_key: Optional[str] = None
    context: dict = Field(default_factory=dict)


class WorkflowTransitionRequest(BaseModel):
    tenant_id: str
    action: str
    actor_id: str
    actor_role: Optional[str] = None
    notes: Optional[str] = None
    context_patch: dict = Field(default_factory=dict)


class WorkflowInstanceResponse(BaseModel):
    id: str
    tenant_id: str
    workflow_definition_id: str
    workflow_code: str
    subject_type: str
    subject_id: str
    business_key: Optional[str]
    current_state: str
    status: str
    context: Optional[dict]
    history: Optional[list]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class DomainEventPublish(BaseModel):
    tenant_id: str
    event_type: str
    source_service: str
    aggregate_type: str
    aggregate_id: str
    payload: dict
    idempotency_key: Optional[str] = None


class DomainEventResponse(BaseModel):
    id: str
    tenant_id: str
    event_type: str
    source_service: str
    aggregate_type: str
    aggregate_id: str
    payload: dict
    idempotency_key: Optional[str]
    status: str
    published_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


app = FastAPI(title="platform-service", version="0.1.0")


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "platform"}


@app.get("/ready")
async def ready():
    return {"ready": True}


def _latest_product(tenant_id: str, product_code: str, db: Session) -> ProductDefinition:
    product = (
        db.query(ProductDefinition)
        .filter(
            ProductDefinition.tenant_id == tenant_id,
            ProductDefinition.product_code == product_code,
            ProductDefinition.status == "active",
        )
        .order_by(ProductDefinition.version.desc())
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Active product definition not found for tenant")
    return product


def _latest_rule_set(tenant_id: str, rule_set_code: str, db: Session) -> RuleSet:
    rule_set = (
        db.query(RuleSet)
        .filter(
            RuleSet.tenant_id == tenant_id,
            RuleSet.rule_set_code == rule_set_code,
            RuleSet.status == "active",
        )
        .order_by(RuleSet.version.desc())
        .first()
    )
    if not rule_set:
        raise HTTPException(status_code=404, detail="Active rule set not found for tenant")
    return rule_set


def _latest_workflow(tenant_id: str, workflow_code: str, db: Session) -> WorkflowDefinition:
    workflow = (
        db.query(WorkflowDefinition)
        .filter(
            WorkflowDefinition.tenant_id == tenant_id,
            WorkflowDefinition.workflow_code == workflow_code,
            WorkflowDefinition.status == "active",
        )
        .order_by(WorkflowDefinition.version.desc())
        .first()
    )
    if not workflow:
        raise HTTPException(status_code=404, detail="Active workflow definition not found for tenant")
    return workflow


def _context_value(context: dict, field: str) -> Any:
    current: Any = context
    for part in field.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _compare(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "exists":
        return actual is not None
    if operator == "not_exists":
        return actual is None
    if operator == "eq":
        return actual == expected
    if operator == "neq":
        return actual != expected
    if operator == "in":
        return actual in (expected or [])
    if operator == "contains":
        return expected in (actual or [])
    if operator == "between":
        low, high = expected
        return actual is not None and low <= actual <= high
    if operator in {"gt", "gte", "lt", "lte"}:
        if actual is None:
            return False
        if operator == "gt":
            return actual > expected
        if operator == "gte":
            return actual >= expected
        if operator == "lt":
            return actual < expected
        if operator == "lte":
            return actual <= expected
    raise HTTPException(status_code=400, detail=f"Unsupported rule operator: {operator}")


def _evaluate_rules(rules: list[dict], context: dict) -> dict:
    passed_rules = []
    failed_rules = []
    score = 0.0
    max_score = 0.0

    for rule in rules:
        field = rule.get("field")
        operator = rule.get("operator", "eq")
        expected = rule.get("value")
        weight = float(rule.get("weight", 1.0))
        max_score += max(weight, 0.0)
        actual = _context_value(context, field) if field else None
        passed = _compare(actual, operator, expected)
        row = {
            "rule_code": rule.get("rule_code"),
            "field": field,
            "operator": operator,
            "expected": expected,
            "actual": actual,
            "message": rule.get("message"),
            "weight": weight,
        }
        if passed:
            score += max(weight, 0.0)
            passed_rules.append(row)
        else:
            failed_rules.append(row)

    score_percent = round((score / max_score) * 100, 2) if max_score else 100.0
    return {
        "passed": not failed_rules,
        "score": round(score, 2),
        "score_percent": score_percent,
        "passed_rules": passed_rules,
        "failed_rules": failed_rules,
    }


@app.post("/products", response_model=ProductDefinitionResponse)
async def create_product(payload: ProductDefinitionCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(ProductDefinition)
        .filter(
            ProductDefinition.tenant_id == payload.tenant_id,
            ProductDefinition.product_code == payload.product_code,
            ProductDefinition.version == payload.version,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Product code and version already exist for tenant")
    product = ProductDefinition(id=str(uuid4()), **payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=List[ProductDefinitionResponse])
async def list_products(
    tenant_id: str = Query(...),
    product_family: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(ProductDefinition).filter(ProductDefinition.tenant_id == tenant_id)
    if product_family:
        query = query.filter(ProductDefinition.product_family == product_family)
    if status:
        query = query.filter(ProductDefinition.status == status)
    return query.order_by(ProductDefinition.product_family.asc(), ProductDefinition.product_code.asc()).all()


@app.get("/products/{product_code}", response_model=ProductDefinitionResponse)
async def get_active_product(product_code: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    return _latest_product(tenant_id, product_code, db)


@app.post("/products/simulate")
async def simulate_product(payload: ProductSimulationRequest, db: Session = Depends(get_db)):
    product = _latest_product(payload.tenant_id, payload.product_code, db)
    context = {
        **payload.attributes,
        "tenant_id": payload.tenant_id,
        "customer_id": payload.customer_id,
        "product_code": payload.product_code,
        "requested_amount": payload.requested_amount,
        "tenure_months": payload.tenure_months,
    }
    eligibility = _evaluate_rules(product.eligibility_rules or [], context)
    pricing_rules = product.pricing_rules or {}
    annual_rate = float(pricing_rules.get("interest_rate_percent", product.parameters.get("interest_rate_percent", 0.0) if product.parameters else 0.0))
    processing_fee_percent = float((product.fee_rules or {}).get("processing_fee_percent", 0.0))
    processing_fee = round(payload.requested_amount * processing_fee_percent / 100, 2)
    monthly_rate = annual_rate / 1200
    if monthly_rate:
        emi = round(payload.requested_amount * monthly_rate * ((1 + monthly_rate) ** payload.tenure_months) / (((1 + monthly_rate) ** payload.tenure_months) - 1), 2)
    else:
        emi = round(payload.requested_amount / payload.tenure_months, 2)
    return {
        "tenant_id": payload.tenant_id,
        "product_code": product.product_code,
        "eligible": eligibility["passed"],
        "eligibility": eligibility,
        "requested_amount": payload.requested_amount,
        "tenure_months": payload.tenure_months,
        "interest_rate_percent": annual_rate,
        "estimated_emi": emi,
        "processing_fee": processing_fee,
        "lifecycle_workflow_code": product.lifecycle_workflow_code,
    }


@app.post("/rulesets", response_model=RuleSetResponse)
async def create_rule_set(payload: RuleSetCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(RuleSet)
        .filter(
            RuleSet.tenant_id == payload.tenant_id,
            RuleSet.rule_set_code == payload.rule_set_code,
            RuleSet.version == payload.version,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Rule set code and version already exist for tenant")
    rule_set = RuleSet(id=str(uuid4()), **payload.model_dump())
    db.add(rule_set)
    db.commit()
    db.refresh(rule_set)
    return rule_set


@app.post("/rulesets/evaluate")
async def evaluate_rule_set(payload: RuleEvaluationRequest, db: Session = Depends(get_db)):
    rules = payload.rules
    rule_set_code = payload.rule_set_code
    if rule_set_code:
        rule_set = _latest_rule_set(payload.tenant_id, rule_set_code, db)
        rules = rule_set.rules
    if rules is None:
        raise HTTPException(status_code=400, detail="Either rule_set_code or inline rules must be provided")
    result = _evaluate_rules(rules, payload.context)
    result["tenant_id"] = payload.tenant_id
    result["rule_set_code"] = rule_set_code
    return result


@app.post("/workflows", response_model=WorkflowDefinitionResponse)
async def create_workflow(payload: WorkflowDefinitionCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(WorkflowDefinition)
        .filter(
            WorkflowDefinition.tenant_id == payload.tenant_id,
            WorkflowDefinition.workflow_code == payload.workflow_code,
            WorkflowDefinition.version == payload.version,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Workflow code and version already exist for tenant")
    workflow = WorkflowDefinition(id=str(uuid4()), **payload.model_dump())
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


@app.post("/workflows/start", response_model=WorkflowInstanceResponse)
async def start_workflow(payload: WorkflowStartRequest, db: Session = Depends(get_db)):
    workflow = _latest_workflow(payload.tenant_id, payload.workflow_code, db)
    history = [
        {
            "action": "start",
            "to_state": workflow.initial_state,
            "actor_id": "system",
            "occurred_at": datetime.utcnow().isoformat(),
            "notes": "Workflow instance started",
        }
    ]
    instance = WorkflowInstance(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        workflow_definition_id=workflow.id,
        workflow_code=workflow.workflow_code,
        subject_type=payload.subject_type,
        subject_id=payload.subject_id,
        business_key=payload.business_key,
        current_state=workflow.initial_state,
        context=payload.context,
        history=history,
    )
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


@app.post("/workflows/instances/{instance_id}/transition", response_model=WorkflowInstanceResponse)
async def transition_workflow(instance_id: str, payload: WorkflowTransitionRequest, db: Session = Depends(get_db)):
    instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id, WorkflowInstance.tenant_id == payload.tenant_id).first()
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found for tenant")
    if instance.status == "completed":
        raise HTTPException(status_code=400, detail="Workflow instance is already completed")
    workflow = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == instance.workflow_definition_id, WorkflowDefinition.tenant_id == payload.tenant_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow definition not found for tenant")

    transition = None
    for item in workflow.transitions:
        if item.get("from_state") == instance.current_state and item.get("action") == payload.action:
            transition = item
            break
    if not transition:
        raise HTTPException(status_code=400, detail="No transition found for current state and action")
    allowed_roles = transition.get("allowed_roles") or []
    if allowed_roles and payload.actor_role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Actor role is not allowed for this transition")

    from_state = instance.current_state
    to_state = transition["to_state"]
    context = dict(instance.context or {})
    context.update(payload.context_patch)
    history = list(instance.history or [])
    history.append(
        {
            "action": payload.action,
            "from_state": from_state,
            "to_state": to_state,
            "actor_id": payload.actor_id,
            "actor_role": payload.actor_role,
            "notes": payload.notes,
            "occurred_at": datetime.utcnow().isoformat(),
        }
    )
    instance.current_state = to_state
    instance.context = context
    instance.history = history
    instance.updated_at = datetime.utcnow()
    if to_state in (workflow.terminal_states or []):
        instance.status = "completed"
        instance.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(instance)
    return instance


@app.get("/workflows/instances", response_model=List[WorkflowInstanceResponse])
async def list_workflow_instances(
    tenant_id: str = Query(...),
    subject_type: Optional[str] = Query(None),
    subject_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(WorkflowInstance).filter(WorkflowInstance.tenant_id == tenant_id)
    if subject_type:
        query = query.filter(WorkflowInstance.subject_type == subject_type)
    if subject_id:
        query = query.filter(WorkflowInstance.subject_id == subject_id)
    if status:
        query = query.filter(WorkflowInstance.status == status)
    return query.order_by(WorkflowInstance.started_at.desc()).all()


@app.post("/events", response_model=DomainEventResponse)
async def publish_event(payload: DomainEventPublish, db: Session = Depends(get_db)):
    if payload.idempotency_key:
        existing = (
            db.query(DomainEvent)
            .filter(DomainEvent.tenant_id == payload.tenant_id, DomainEvent.idempotency_key == payload.idempotency_key)
            .first()
        )
        if existing:
            return existing
    event = DomainEvent(id=str(uuid4()), **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/events", response_model=List[DomainEventResponse])
async def list_events(
    tenant_id: str = Query(...),
    event_type: Optional[str] = Query(None),
    aggregate_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(DomainEvent).filter(DomainEvent.tenant_id == tenant_id)
    if event_type:
        query = query.filter(DomainEvent.event_type == event_type)
    if aggregate_id:
        query = query.filter(DomainEvent.aggregate_id == aggregate_id)
    if status:
        query = query.filter(DomainEvent.status == status)
    return query.order_by(DomainEvent.published_at.desc()).all()


@app.post("/events/{event_id}/mark-processed", response_model=DomainEventResponse)
async def mark_event_processed(event_id: str, tenant_id: str = Query(...), db: Session = Depends(get_db)):
    event = db.query(DomainEvent).filter(DomainEvent.id == event_id, DomainEvent.tenant_id == tenant_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Domain event not found for tenant")
    event.status = "processed"
    event.processed_at = datetime.utcnow()
    db.commit()
    db.refresh(event)
    return event


@app.get("/")
async def root():
    return {"service": "platform", "version": "0.1.0"}
