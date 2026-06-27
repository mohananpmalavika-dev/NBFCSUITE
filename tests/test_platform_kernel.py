import asyncio
import os
from pathlib import Path


os.environ["DATABASE_URL"] = "sqlite:///C:/tmp/platform_kernel_test.db"

db_path = Path("C:/tmp/platform_kernel_test.db")
if db_path.exists():
    db_path.unlink()

from services.platform.app.main import (
    Base as PlatformBase,
    DomainEventPublish,
    ProductDefinitionCreate,
    ProductSimulationRequest,
    RuleEvaluationRequest,
    RuleSetCreate,
    SessionLocal as PlatformSessionLocal,
    WorkflowDefinitionCreate,
    WorkflowStartRequest,
    WorkflowTransitionRequest,
    create_product,
    create_rule_set,
    create_workflow,
    engine as platform_engine,
    evaluate_rule_set,
    list_events,
    mark_event_processed,
    publish_event,
    simulate_product,
    start_workflow,
    transition_workflow,
)


def run(coro):
    return asyncio.run(coro)


def test_product_factory_rule_engine_and_pricing_simulation():
    PlatformBase.metadata.drop_all(bind=platform_engine)
    PlatformBase.metadata.create_all(bind=platform_engine)
    db = PlatformSessionLocal()
    try:
        rule_set = run(
            create_rule_set(
                RuleSetCreate(
                    tenant_id="tenant-a",
                    rule_set_code="PL-ELIGIBILITY",
                    rule_set_name="Personal Loan Eligibility",
                    rules=[
                        {"rule_code": "MIN_SCORE", "field": "credit_score", "operator": "gte", "value": 700, "weight": 2},
                        {"rule_code": "MAX_AMOUNT", "field": "requested_amount", "operator": "lte", "value": 500000, "weight": 1},
                    ],
                ),
                db,
            )
        )
        assert rule_set.rule_set_code == "PL-ELIGIBILITY"

        evaluation = run(
            evaluate_rule_set(
                RuleEvaluationRequest(
                    tenant_id="tenant-a",
                    rule_set_code="PL-ELIGIBILITY",
                    context={"credit_score": 740, "requested_amount": 300000},
                ),
                db,
            )
        )
        assert evaluation["passed"] is True
        assert evaluation["score_percent"] == 100

        product = run(
            create_product(
                ProductDefinitionCreate(
                    tenant_id="tenant-a",
                    product_code="PL-SALARIED",
                    product_name="Salaried Personal Loan",
                    product_family="lending",
                    status="active",
                    parameters={"interest_rate_percent": 14.0},
                    eligibility_rules=rule_set.rules,
                    pricing_rules={"interest_rate_percent": 13.5},
                    fee_rules={"processing_fee_percent": 1.0},
                    lifecycle_workflow_code="LOAN-APPROVAL",
                ),
                db,
            )
        )
        assert product.status == "active"

        simulation = run(
            simulate_product(
                ProductSimulationRequest(
                    tenant_id="tenant-a",
                    product_code="PL-SALARIED",
                    customer_id="customer-1",
                    requested_amount=300000,
                    tenure_months=24,
                    attributes={"credit_score": 740},
                ),
                db,
            )
        )
        assert simulation["eligible"] is True
        assert simulation["estimated_emi"] > 0
        assert simulation["processing_fee"] == 3000
    finally:
        db.close()


def test_workflow_definition_instance_transition_and_completion():
    PlatformBase.metadata.drop_all(bind=platform_engine)
    PlatformBase.metadata.create_all(bind=platform_engine)
    db = PlatformSessionLocal()
    try:
        workflow = run(
            create_workflow(
                WorkflowDefinitionCreate(
                    tenant_id="tenant-a",
                    workflow_code="GOLD-LOAN-APPROVAL",
                    workflow_name="Gold Loan Approval",
                    initial_state="draft",
                    terminal_states=["approved", "rejected"],
                    transitions=[
                        {"from_state": "draft", "action": "submit", "to_state": "valuation", "allowed_roles": ["loan_officer"]},
                        {"from_state": "valuation", "action": "approve", "to_state": "approved", "allowed_roles": ["branch_manager"]},
                    ],
                ),
                db,
            )
        )
        assert workflow.initial_state == "draft"

        instance = run(
            start_workflow(
                WorkflowStartRequest(
                    tenant_id="tenant-a",
                    workflow_code="GOLD-LOAN-APPROVAL",
                    subject_type="gold_loan",
                    subject_id="gl-1",
                    business_key="GL-1",
                    context={"requested_amount": 150000},
                ),
                db,
            )
        )
        assert instance.current_state == "draft"

        submitted = run(
            transition_workflow(
                instance.id,
                WorkflowTransitionRequest(
                    tenant_id="tenant-a",
                    action="submit",
                    actor_id="employee-1",
                    actor_role="loan_officer",
                ),
                db,
            )
        )
        assert submitted.current_state == "valuation"

        approved = run(
            transition_workflow(
                instance.id,
                WorkflowTransitionRequest(
                    tenant_id="tenant-a",
                    action="approve",
                    actor_id="manager-1",
                    actor_role="branch_manager",
                    notes="Purity and LTV verified",
                    context_patch={"approved_amount": 140000},
                ),
                db,
            )
        )
        assert approved.status == "completed"
        assert approved.current_state == "approved"
        assert approved.context["approved_amount"] == 140000
    finally:
        db.close()


def test_domain_event_outbox_idempotency_and_processing():
    PlatformBase.metadata.drop_all(bind=platform_engine)
    PlatformBase.metadata.create_all(bind=platform_engine)
    db = PlatformSessionLocal()
    try:
        payload = DomainEventPublish(
            tenant_id="tenant-a",
            event_type="loan.application.approved",
            source_service="los",
            aggregate_type="loan_application",
            aggregate_id="app-1",
            payload={"approved_amount": 250000},
            idempotency_key="los-app-1-approved",
        )
        first = run(publish_event(payload, db))
        second = run(publish_event(payload, db))
        assert first.id == second.id

        events = run(list_events(tenant_id="tenant-a", event_type="loan.application.approved", aggregate_id=None, status=None, db=db))
        assert len(events) == 1

        processed = run(mark_event_processed(first.id, tenant_id="tenant-a", db=db))
        assert processed.status == "processed"
    finally:
        db.close()
