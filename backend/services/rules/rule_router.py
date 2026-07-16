"""
Business Rules API Router

Endpoints for rule management and execution
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from backend.shared.database.connection import get_db
from backend.shared.auth.dependencies import get_current_user, get_tenant_id
from backend.services.rules.rule_models import (
    RuleSet, DecisionRule, ValidationRule, CalculationRule,
    RoutingRule, PricingRule, EligibilityRule, DecisionTable,
    RuleTemplate, RuleExecutionContext, RuleExecutionResult,
    FORMULA_FUNCTIONS, ExecutionEngineConfig, ExecutionMode,
    ExecutionStrategy, RulePriority, BatchSchedule, RuleChain,
    RuleChainStep, RuleChainExecutionResult, ExecutionHistory,
    RuleVersion, VersionComparison, RuleTestCase, RuleTestResult,
    ImpactAssessment, RuleClone, AuditTrail, VersionStatus, ChangeType
)
from backend.services.rules.rule_engine import RuleEngine


router = APIRouter(prefix="/api/rules")


# ==================== RULESET MANAGEMENT ====================

@router.post("/rulesets", tags=["Rulesets"])
def create_ruleset(
    ruleset: RuleSet,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create new ruleset"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Generate ID if not provided
    if not ruleset.ruleset_id:
        ruleset.ruleset_id = f"ruleset_{uuid.uuid4().hex[:8]}"
    
    ruleset.created_at = datetime.utcnow()
    ruleset.created_by = current_user['id']
    
    # Store in database as template
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=ruleset.ruleset_id,
        template_name=ruleset.ruleset_name,
        template_type='ruleset',
        definition={'ruleset': ruleset.dict()},
        is_active=ruleset.is_active,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": ruleset.dict()
    }


@router.get("/rulesets", tags=["Rulesets"])
def list_rulesets(
    entity_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List all rulesets"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'ruleset'
    )
    
    if is_active is not None:
        query = query.filter(WorkflowTemplate.is_active == is_active)
    
    templates = query.all()
    
    rulesets = []
    for template in templates:
        ruleset_data = template.definition.get('ruleset', {})
        
        # Filter by entity_type if specified
        if entity_type and ruleset_data.get('entity_type') != entity_type:
            continue
        
        rulesets.append({
            'ruleset_id': template.template_key,
            'ruleset_name': template.template_name,
            'entity_type': ruleset_data.get('entity_type'),
            'version': ruleset_data.get('version'),
            'is_active': template.is_active,
            'created_at': template.created_at,
            'rule_counts': {
                'decision': len(ruleset_data.get('decision_rules', [])),
                'validation': len(ruleset_data.get('validation_rules', [])),
                'calculation': len(ruleset_data.get('calculation_rules', [])),
                'routing': len(ruleset_data.get('routing_rules', [])),
                'pricing': len(ruleset_data.get('pricing_rules', [])),
                'eligibility': len(ruleset_data.get('eligibility_rules', [])),
                'decision_tables': len(ruleset_data.get('decision_tables', []))
            }
        })
    
    return {
        "success": True,
        "data": rulesets
    }


@router.get("/rulesets/{ruleset_id}", tags=["Rulesets"])
def get_ruleset(
    ruleset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get ruleset details"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    return {
        "success": True,
        "data": template.definition.get('ruleset', {})
    }


@router.put("/rulesets/{ruleset_id}", tags=["Rulesets"])
def update_ruleset(
    ruleset_id: str,
    ruleset: RuleSet,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update ruleset"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset.updated_at = datetime.utcnow()
    template.definition = {'ruleset': ruleset.dict()}
    template.is_active = ruleset.is_active
    template.updated_by = current_user['id']
    
    db.commit()
    
    return {
        "success": True,
        "data": ruleset.dict()
    }


@router.delete("/rulesets/{ruleset_id}", tags=["Rulesets"])
def delete_ruleset(
    ruleset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Delete ruleset"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    template.is_deleted = True
    db.commit()
    
    return {
        "success": True,
        "message": "Ruleset deleted successfully"
    }


# ==================== RULE EXECUTION ====================

@router.post("/execute", tags=["Execution"])
def execute_rules(
    context: RuleExecutionContext,
    ruleset_id: str,
    execution_mode: Optional[ExecutionMode] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Execute rules with specified execution mode"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Get ruleset
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset_data = template.definition.get('ruleset', {})
    ruleset = RuleSet(**ruleset_data)
    
    # Execute rules with mode support
    engine = RuleEngine()
    result = engine.execute_with_mode(ruleset, context, execution_mode)
    
    # Store execution history
    history = ExecutionHistory(
        history_id=f"hist_{uuid.uuid4().hex[:8]}",
        execution_id=result.execution_id,
        ruleset_id=ruleset_id,
        execution_mode=execution_mode or ExecutionMode.ON_DEMAND,
        execution_type="single",
        started_at=result.executed_at,
        completed_at=datetime.utcnow(),
        execution_time_ms=result.execution_time_ms,
        status="success" if result.success else "failure",
        rules_executed_count=len(result.rules_executed),
        rules_passed_count=len(result.rules_matched),
        rules_failed_count=len(result.validation_errors),
        input_data_sample=context.data,
        output_data_sample=result.output_data,
        error_count=len(result.validation_errors),
        tenant_id=tenant_id,
        user_id=current_user['id'],
        triggered_by="api"
    )
    
    # Store history in database
    _store_execution_history(db, tenant_id, history)
    
    return {
        "success": True,
        "data": result.dict()
    }


@router.post("/validate", tags=["Execution"])
def validate_data(
    context: RuleExecutionContext,
    ruleset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Validate data using validation rules"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Get ruleset
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset_data = template.definition.get('ruleset', {})
    ruleset = RuleSet(**ruleset_data)
    
    # Execute only validation rules
    engine = RuleEngine()
    result = RuleExecutionResult(
        execution_id=f"valid_{datetime.utcnow().timestamp()}",
        ruleset_id=ruleset_id,
        context_id=context.context_id,
        success=True,
        rules_executed=[],
        rules_matched=[],
        actions_executed=[],
        output_data=context.data.copy(),
        execution_time_ms=0,
        executed_at=datetime.utcnow()
    )
    
    engine._execute_validation_rules(ruleset.validation_rules, context, result)
    
    return {
        "success": len(result.validation_errors) == 0,
        "data": {
            "is_valid": len(result.validation_errors) == 0,
            "errors": result.validation_errors,
            "warnings": result.validation_warnings
        }
    }


# ==================== RULE TEMPLATES ====================

@router.get("/templates", tags=["Templates"])
def get_rule_templates(
    rule_type: Optional[str] = None,
    category: Optional[str] = None
):
    """Get rule templates"""
    templates = get_predefined_templates()
    
    # Filter by type
    if rule_type:
        templates = [t for t in templates if t['rule_type'] == rule_type]
    
    # Filter by category
    if category:
        templates = [t for t in templates if t.get('category') == category]
    
    return {
        "success": True,
        "data": templates
    }


@router.get("/formula-functions", tags=["Formulas"])
def get_formula_functions():
    """Get available formula functions"""
    return {
        "success": True,
        "data": [f.dict() for f in FORMULA_FUNCTIONS]
    }


# ==================== HELPER FUNCTIONS ====================

def get_predefined_templates():
    """Get predefined rule templates"""
    return [
        {
            "template_id": "age_validation",
            "template_name": "Age Validation",
            "description": "Validate minimum age requirement",
            "rule_type": "validation",
            "category": "Eligibility",
            "template_structure": {
                "conditions": {
                    "group_id": "g1",
                    "logical_operator": "and",
                    "conditions": [
                        {
                            "condition_id": "c1",
                            "field": "age",
                            "field_type": "number",
                            "operator": "greater_than_or_equal",
                            "value": 21
                        }
                    ]
                },
                "error_message": "Minimum age is 21 years",
                "severity": "error"
            }
        },
        {
            "template_id": "loan_eligibility",
            "template_name": "Loan Eligibility",
            "description": "Check loan eligibility criteria",
            "rule_type": "eligibility",
            "category": "Lending",
            "template_structure": {
                "criteria": [
                    {
                        "group_id": "age_check",
                        "logical_operator": "and",
                        "conditions": [
                            {
                                "condition_id": "c1",
                                "field": "age",
                                "field_type": "number",
                                "operator": "greater_than_or_equal",
                                "value": 21
                            }
                        ]
                    },
                    {
                        "group_id": "income_check",
                        "logical_operator": "and",
                        "conditions": [
                            {
                                "condition_id": "c2",
                                "field": "monthly_income",
                                "field_type": "number",
                                "operator": "greater_than_or_equal",
                                "value": 25000
                            }
                        ]
                    }
                ],
                "all_must_pass": True
            }
        },
        {
            "template_id": "interest_calculation",
            "template_name": "Interest Calculation",
            "description": "Calculate interest amount",
            "rule_type": "calculation",
            "category": "Financial",
            "template_structure": {
                "target_field": "interest_amount",
                "formula": "principal * rate / 100 * tenure",
                "formula_fields": ["principal", "rate", "tenure"],
                "decimal_places": 2
            }
        },
        {
            "template_id": "tiered_pricing",
            "template_name": "Tiered Pricing",
            "description": "Volume-based pricing tiers",
            "rule_type": "pricing",
            "category": "Pricing",
            "template_structure": {
                "base_price_field": "unit_price",
                "tiers": [
                    {
                        "conditions": {
                            "group_id": "tier1",
                            "logical_operator": "and",
                            "conditions": [
                                {
                                    "condition_id": "c1",
                                    "field": "quantity",
                                    "field_type": "number",
                                    "operator": "greater_than",
                                    "value": 100
                                }
                            ]
                        },
                        "multiplier": 0.9,
                        "priority": 1
                    }
                ]
            }
        }
    ]



# ==================== EXECUTION ENGINE CONFIGURATION ====================

@router.post("/execution-config", tags=["Execution Engine"])
def create_execution_config(
    config: ExecutionEngineConfig,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create execution engine configuration"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Generate ID if not provided
    if not config.config_id:
        config.config_id = f"config_{uuid.uuid4().hex[:8]}"
    
    config.created_at = datetime.utcnow()
    
    # Store in database
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=config.config_id,
        template_name=config.config_name,
        template_type='execution_config',
        definition={'config': config.dict()},
        is_active=config.is_active,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": config.dict()
    }


@router.get("/execution-config/{config_id}", tags=["Execution Engine"])
def get_execution_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get execution config details"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == config_id,
        WorkflowTemplate.template_type == 'execution_config'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Execution config not found")
    
    return {
        "success": True,
        "data": template.definition.get('config', {})
    }


@router.put("/execution-config/{config_id}", tags=["Execution Engine"])
def update_execution_config(
    config_id: str,
    config: ExecutionEngineConfig,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update execution config"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == config_id,
        WorkflowTemplate.template_type == 'execution_config'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Execution config not found")
    
    config.updated_at = datetime.utcnow()
    template.definition = {'config': config.dict()}
    template.is_active = config.is_active
    template.updated_by = current_user['id']
    
    db.commit()
    
    return {
        "success": True,
        "data": config.dict()
    }


# ==================== RULE CHAINS ====================

@router.post("/chains", tags=["Rule Chains"])
def create_rule_chain(
    chain: RuleChain,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create new rule chain"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Generate ID if not provided
    if not chain.chain_id:
        chain.chain_id = f"chain_{uuid.uuid4().hex[:8]}"
    
    chain.created_at = datetime.utcnow()
    chain.created_by = current_user['id']
    
    # Store in database
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=chain.chain_id,
        template_name=chain.chain_name,
        template_type='rule_chain',
        definition={'chain': chain.dict()},
        is_active=chain.is_active,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": chain.dict()
    }


@router.get("/chains", tags=["Rule Chains"])
def list_rule_chains(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List all rule chains"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'rule_chain'
    )
    
    if is_active is not None:
        query = query.filter(WorkflowTemplate.is_active == is_active)
    
    templates = query.all()
    
    chains = []
    for template in templates:
        chain_data = template.definition.get('chain', {})
        
        chains.append({
            'chain_id': template.template_key,
            'chain_name': template.template_name,
            'step_count': len(chain_data.get('steps', [])),
            'execution_strategy': chain_data.get('execution_strategy'),
            'is_active': template.is_active,
            'created_at': template.created_at,
        })
    
    return {
        "success": True,
        "data": chains
    }


@router.get("/chains/{chain_id}", tags=["Rule Chains"])
def get_rule_chain(
    chain_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get rule chain details"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == chain_id,
        WorkflowTemplate.template_type == 'rule_chain'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Rule chain not found")
    
    return {
        "success": True,
        "data": template.definition.get('chain', {})
    }


@router.put("/chains/{chain_id}", tags=["Rule Chains"])
def update_rule_chain(
    chain_id: str,
    chain: RuleChain,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update rule chain"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == chain_id,
        WorkflowTemplate.template_type == 'rule_chain'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Rule chain not found")
    
    template.definition = {'chain': chain.dict()}
    template.is_active = chain.is_active
    template.updated_by = current_user['id']
    
    db.commit()
    
    return {
        "success": True,
        "data": chain.dict()
    }


@router.delete("/chains/{chain_id}", tags=["Rule Chains"])
def delete_rule_chain(
    chain_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Delete rule chain"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == chain_id,
        WorkflowTemplate.template_type == 'rule_chain'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Rule chain not found")
    
    template.is_deleted = True
    db.commit()
    
    return {
        "success": True,
        "message": "Rule chain deleted successfully"
    }


@router.post("/chains/{chain_id}/execute", tags=["Rule Chains"])
def execute_rule_chain(
    chain_id: str,
    context: RuleExecutionContext,
    ruleset_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Execute a rule chain"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Get rule chain
    chain_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == chain_id,
        WorkflowTemplate.template_type == 'rule_chain'
    ).first()
    
    if not chain_template:
        raise HTTPException(status_code=404, detail="Rule chain not found")
    
    chain_data = chain_template.definition.get('chain', {})
    chain = RuleChain(**chain_data)
    
    # Get ruleset
    ruleset_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not ruleset_template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset_data = ruleset_template.definition.get('ruleset', {})
    ruleset = RuleSet(**ruleset_data)
    
    # Execute chain
    engine = RuleEngine()
    result = engine.execute_rule_chain(ruleset, chain, context)
    
    # Store execution history
    history = ExecutionHistory(
        history_id=f"hist_{uuid.uuid4().hex[:8]}",
        execution_id=result.execution_id,
        ruleset_id=ruleset_id,
        execution_mode=ExecutionMode.ON_DEMAND,
        execution_type="chain",
        started_at=result.executed_at,
        completed_at=datetime.utcnow(),
        execution_time_ms=result.execution_time_ms,
        status="success" if result.success else "failure",
        rules_executed_count=result.steps_completed,
        rules_passed_count=result.steps_completed,
        rules_failed_count=result.steps_failed,
        input_data_sample=context.data,
        output_data_sample=result.final_output,
        error_count=result.steps_failed,
        tenant_id=tenant_id,
        user_id=current_user['id'],
        triggered_by="api"
    )
    
    _store_execution_history(db, tenant_id, history)
    
    return {
        "success": True,
        "data": result.dict()
    }


# ==================== BATCH SCHEDULES ====================

@router.post("/batch-schedules", tags=["Batch Execution"])
def create_batch_schedule(
    schedule: BatchSchedule,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create batch execution schedule"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Generate ID if not provided
    if not schedule.schedule_id:
        schedule.schedule_id = f"schedule_{uuid.uuid4().hex[:8]}"
    
    schedule.created_at = datetime.utcnow()
    schedule.created_by = current_user['id']
    
    # Store in database
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=schedule.schedule_id,
        template_name=schedule.schedule_name,
        template_type='batch_schedule',
        definition={'schedule': schedule.dict()},
        is_active=schedule.enabled,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": schedule.dict()
    }


@router.get("/batch-schedules", tags=["Batch Execution"])
def list_batch_schedules(
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List all batch schedules"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'batch_schedule'
    )
    
    if enabled is not None:
        query = query.filter(WorkflowTemplate.is_active == enabled)
    
    templates = query.all()
    
    schedules = []
    for template in templates:
        schedule_data = template.definition.get('schedule', {})
        
        schedules.append({
            'schedule_id': template.template_key,
            'schedule_name': template.template_name,
            'ruleset_id': schedule_data.get('ruleset_id'),
            'cron_expression': schedule_data.get('cron_expression'),
            'enabled': template.is_active,
            'last_execution_at': schedule_data.get('last_execution_at'),
            'last_execution_status': schedule_data.get('last_execution_status'),
            'next_execution_at': schedule_data.get('next_execution_at'),
            'created_at': template.created_at,
        })
    
    return {
        "success": True,
        "data": schedules
    }


@router.get("/batch-schedules/{schedule_id}", tags=["Batch Execution"])
def get_batch_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get batch schedule details"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == schedule_id,
        WorkflowTemplate.template_type == 'batch_schedule'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Batch schedule not found")
    
    return {
        "success": True,
        "data": template.definition.get('schedule', {})
    }


@router.put("/batch-schedules/{schedule_id}", tags=["Batch Execution"])
def update_batch_schedule(
    schedule_id: str,
    schedule: BatchSchedule,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update batch schedule"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == schedule_id,
        WorkflowTemplate.template_type == 'batch_schedule'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Batch schedule not found")
    
    template.definition = {'schedule': schedule.dict()}
    template.is_active = schedule.enabled
    template.updated_by = current_user['id']
    
    db.commit()
    
    return {
        "success": True,
        "data": schedule.dict()
    }


@router.delete("/batch-schedules/{schedule_id}", tags=["Batch Execution"])
def delete_batch_schedule(
    schedule_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Delete batch schedule"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == schedule_id,
        WorkflowTemplate.template_type == 'batch_schedule'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Batch schedule not found")
    
    template.is_deleted = True
    db.commit()
    
    return {
        "success": True,
        "message": "Batch schedule deleted successfully"
    }


# ==================== EXECUTION HISTORY ====================

@router.get("/execution-history", tags=["Execution History"])
def get_execution_history(
    ruleset_id: Optional[str] = None,
    execution_mode: Optional[ExecutionMode] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get execution history"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'execution_history'
    )
    
    # Apply filters
    if ruleset_id or execution_mode or status:
        templates = query.all()
        filtered_histories = []
        
        for template in templates:
            history_data = template.definition.get('history', {})
            
            if ruleset_id and history_data.get('ruleset_id') != ruleset_id:
                continue
            if execution_mode and history_data.get('execution_mode') != execution_mode:
                continue
            if status and history_data.get('status') != status:
                continue
            
            filtered_histories.append(history_data)
        
        # Apply pagination
        paginated = filtered_histories[offset:offset + limit]
        
        return {
            "success": True,
            "data": {
                "items": paginated,
                "total": len(filtered_histories),
                "limit": limit,
                "offset": offset
            }
        }
    else:
        # No filters, just paginate
        templates = query.order_by(WorkflowTemplate.created_at.desc()).offset(offset).limit(limit).all()
        total = query.count()
        
        histories = [template.definition.get('history', {}) for template in templates]
        
        return {
            "success": True,
            "data": {
                "items": histories,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        }


@router.get("/execution-history/{execution_id}", tags=["Execution History"])
def get_execution_history_detail(
    execution_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get detailed execution history"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == execution_id,
        WorkflowTemplate.template_type == 'execution_history'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Execution history not found")
    
    return {
        "success": True,
        "data": template.definition.get('history', {})
    }


# ==================== HELPER FUNCTIONS ====================

def _store_execution_history(db: Session, tenant_id: int, history: ExecutionHistory):
    """Store execution history in database"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=history.execution_id,
        template_name=f"Execution {history.execution_id}",
        template_type='execution_history',
        definition={'history': history.dict()},
        is_active=True,
        created_by=history.user_id
    )
    
    db.add(template)
    db.commit()


# ==================== DECISION TABLES ====================

@router.post("/decision-tables", tags=["Decision Tables"])
def create_decision_table(
    table: DecisionTable,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create new decision table"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Generate ID if not provided
    if not table.table_id:
        table.table_id = f"table_{uuid.uuid4().hex[:8]}"
    
    table.created_at = datetime.utcnow()
    
    # Store in database as template
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=table.table_id,
        template_name=table.table_name,
        template_type='decision_table',
        definition={'table': table.dict()},
        is_active=table.is_active,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": table.dict()
    }


@router.get("/decision-tables", tags=["Decision Tables"])
def list_decision_tables(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List all decision tables"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'decision_table'
    )
    
    if is_active is not None:
        query = query.filter(WorkflowTemplate.is_active == is_active)
    
    templates = query.all()
    
    tables = []
    for template in templates:
        table_data = template.definition.get('table', {})
        
        tables.append({
            'table_id': template.template_key,
            'table_name': template.template_name,
            'version': table_data.get('version'),
            'column_count': len(table_data.get('columns', [])),
            'row_count': len(table_data.get('rows', [])),
            'is_active': template.is_active,
            'created_at': template.created_at,
        })
    
    return {
        "success": True,
        "data": tables
    }


@router.get("/decision-tables/{table_id}", tags=["Decision Tables"])
def get_decision_table(
    table_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get decision table details"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == table_id,
        WorkflowTemplate.template_type == 'decision_table'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Decision table not found")
    
    return {
        "success": True,
        "data": template.definition.get('table', {})
    }


@router.put("/decision-tables/{table_id}", tags=["Decision Tables"])
def update_decision_table(
    table_id: str,
    table: DecisionTable,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update decision table"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == table_id,
        WorkflowTemplate.template_type == 'decision_table'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Decision table not found")
    
    table.updated_at = datetime.utcnow()
    template.definition = {'table': table.dict()}
    template.is_active = table.is_active
    template.updated_by = current_user['id']
    
    db.commit()
    
    return {
        "success": True,
        "data": table.dict()
    }


@router.delete("/decision-tables/{table_id}", tags=["Decision Tables"])
def delete_decision_table(
    table_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Delete decision table"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == table_id,
        WorkflowTemplate.template_type == 'decision_table'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Decision table not found")
    
    template.is_deleted = True
    db.commit()
    
    return {
        "success": True,
        "message": "Decision table deleted successfully"
    }


@router.post("/decision-tables/{table_id}/evaluate", tags=["Decision Tables"])
def evaluate_decision_table(
    table_id: str,
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Evaluate decision table with input data"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Get decision table
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == table_id,
        WorkflowTemplate.template_type == 'decision_table'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Decision table not found")
    
    table_data = template.definition.get('table', {})
    table = DecisionTable(**table_data)
    
    # Evaluate table
    engine = RuleEngine()
    result = engine.evaluate_decision_table(table, data)
    
    return {
        "success": True,
        "data": result.dict()
    }


@router.post("/decision-tables/{table_id}/test", tags=["Decision Tables"])
def test_decision_table(
    table_id: str,
    test_cases: List[dict],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Test decision table with multiple test cases"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Get decision table
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == table_id,
        WorkflowTemplate.template_type == 'decision_table'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Decision table not found")
    
    table_data = template.definition.get('table', {})
    table = DecisionTable(**table_data)
    
    # Evaluate each test case
    engine = RuleEngine()
    results = []
    
    for i, test_case in enumerate(test_cases):
        result = engine.evaluate_decision_table(table, test_case.get('data', {}))
        results.append({
            'test_case_index': i,
            'test_case_name': test_case.get('name', f'Test Case {i+1}'),
            'input': test_case.get('data', {}),
            'result': result.dict()
        })
    
    return {
        "success": True,
        "data": {
            'total_cases': len(test_cases),
            'results': results
        }
    }


@router.get("/decision-tables/templates/predefined", tags=["Decision Tables"])
def get_decision_table_templates():
    """Get predefined decision table templates"""
    templates = [
        {
            "template_id": "interest_rate_matrix",
            "template_name": "Interest Rate Matrix",
            "description": "Determine interest rate based on CIBIL score, salary, and tenure",
            "category": "Lending",
            "example": {
                "columns": [
                    {
                        "column_id": "col1",
                        "column_name": "CIBIL Score",
                        "column_type": "input",
                        "field_name": "cibil_score",
                        "field_type": "number",
                        "operator": "between"
                    },
                    {
                        "column_id": "col2",
                        "column_name": "Salary Range",
                        "column_type": "input",
                        "field_name": "monthly_salary",
                        "field_type": "number",
                        "operator": "greater_than_or_equal"
                    },
                    {
                        "column_id": "col3",
                        "column_name": "Tenure (months)",
                        "column_type": "input",
                        "field_name": "tenure",
                        "field_type": "number",
                        "operator": "between"
                    },
                    {
                        "column_id": "col4",
                        "column_name": "Interest Rate",
                        "column_type": "output",
                        "field_name": "interest_rate",
                        "field_type": "number"
                    }
                ],
                "rows": [
                    {
                        "row_id": "row1",
                        "row_order": 1,
                        "cells": [
                            {"column_id": "col1", "value_min": 750, "value_max": 900, "is_range": True},
                            {"column_id": "col2", "value": 100000},
                            {"column_id": "col3", "value_min": 12, "value_max": 36, "is_range": True},
                            {"column_id": "col4", "value": 10.5}
                        ]
                    },
                    {
                        "row_id": "row2",
                        "row_order": 2,
                        "cells": [
                            {"column_id": "col1", "value_min": 750, "value_max": 900, "is_range": True},
                            {"column_id": "col2", "value": 50000},
                            {"column_id": "col3", "value_min": 12, "value_max": 36, "is_range": True},
                            {"column_id": "col4", "value": 11.5}
                        ]
                    },
                    {
                        "row_id": "row3",
                        "row_order": 3,
                        "cells": [
                            {"column_id": "col1", "value_min": 700, "value_max": 749, "is_range": True},
                            {"column_id": "col2", "value": 100000},
                            {"column_id": "col3", "value_min": 12, "value_max": 36, "is_range": True},
                            {"column_id": "col4", "value": 12.0}
                        ]
                    },
                    {
                        "row_id": "row4",
                        "row_order": 4,
                        "cells": [
                            {"column_id": "col1", "value": 700, "is_range": False},
                            {"column_id": "col2", "is_any": True},
                            {"column_id": "col3", "is_any": True},
                            {"column_id": "col4", "value": "Reject", "is_reject": True}
                        ]
                    }
                ]
            }
        },
        {
            "template_id": "loan_eligibility_matrix",
            "template_name": "Loan Eligibility Matrix",
            "description": "Determine maximum loan amount based on age, income, employment, and CIBIL",
            "category": "Lending",
            "example": {
                "columns": [
                    {
                        "column_id": "col1",
                        "column_name": "Age",
                        "column_type": "input",
                        "field_name": "age",
                        "field_type": "number",
                        "operator": "between"
                    },
                    {
                        "column_id": "col2",
                        "column_name": "Income",
                        "column_type": "input",
                        "field_name": "monthly_income",
                        "field_type": "number",
                        "operator": "greater_than"
                    },
                    {
                        "column_id": "col3",
                        "column_name": "Employment",
                        "column_type": "input",
                        "field_name": "employment_type",
                        "field_type": "string",
                        "operator": "equals"
                    },
                    {
                        "column_id": "col4",
                        "column_name": "CIBIL",
                        "column_type": "input",
                        "field_name": "cibil_score",
                        "field_type": "number",
                        "operator": "greater_than"
                    },
                    {
                        "column_id": "col5",
                        "column_name": "Max Loan Multiplier",
                        "column_type": "output",
                        "field_name": "loan_multiplier",
                        "field_type": "number"
                    }
                ],
                "rows": [
                    {
                        "row_id": "row1",
                        "row_order": 1,
                        "cells": [
                            {"column_id": "col1", "value_min": 21, "value_max": 30, "is_range": True},
                            {"column_id": "col2", "value": 50000},
                            {"column_id": "col3", "value": "Salaried"},
                            {"column_id": "col4", "value": 700},
                            {"column_id": "col5", "value": 10}
                        ]
                    },
                    {
                        "row_id": "row2",
                        "row_order": 2,
                        "cells": [
                            {"column_id": "col1", "value_min": 31, "value_max": 50, "is_range": True},
                            {"column_id": "col2", "value": 50000},
                            {"column_id": "col3", "value": "Salaried"},
                            {"column_id": "col4", "value": 700},
                            {"column_id": "col5", "value": 15}
                        ]
                    },
                    {
                        "row_id": "row3",
                        "row_order": 3,
                        "cells": [
                            {"column_id": "col1", "value_min": 51, "value_max": 60, "is_range": True},
                            {"column_id": "col2", "value": 50000},
                            {"column_id": "col3", "value": "Salaried"},
                            {"column_id": "col4", "value": 700},
                            {"column_id": "col5", "value": 10}
                        ]
                    }
                ]
            }
        }
    ]
    
    return {
        "success": True,
        "data": templates
    }



# ==================== VERSION MANAGEMENT ====================

@router.post("/versions", tags=["Version Management"])
def create_version(
    ruleset_id: str,
    version_name: str,
    change_summary: str,
    change_type: str = "modified",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create new version of ruleset"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.version_manager import version_manager
    from backend.services.rules.rule_models import RuleVersion, ChangeType
    
    # Get current ruleset
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset_data = template.definition.get('ruleset', {})
    ruleset = RuleSet(**ruleset_data)
    
    # Create version
    try:
        version = version_manager.create_version(
            ruleset=ruleset,
            version_name=version_name,
            change_summary=change_summary,
            change_type=ChangeType(change_type),
            user_id=current_user['id']
        )
        
        # Store version in database
        version_template = WorkflowTemplate(
            tenant_id=tenant_id,
            template_key=version.version_id,
            template_name=version_name,
            template_type='rule_version',
            definition={'version': version.dict()},
            is_active=True,
            created_by=current_user['id']
        )
        
        db.add(version_template)
        db.commit()
        
        return {
            "success": True,
            "data": version.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/versions", tags=["Version Management"])
def list_versions(
    ruleset_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List all versions of a ruleset"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'rule_version'
    )
    
    templates = query.all()
    
    # Filter by ruleset_id and status
    versions = []
    for template in templates:
        version_data = template.definition.get('version', {})
        
        if version_data.get('ruleset_id') != ruleset_id:
            continue
        
        if status and version_data.get('status') != status:
            continue
        
        versions.append({
            'version_id': template.template_key,
            'version_number': version_data.get('version_number'),
            'version_name': version_data.get('version_name'),
            'status': version_data.get('status'),
            'change_type': version_data.get('change_type'),
            'change_summary': version_data.get('change_summary'),
            'created_at': version_data.get('created_at'),
            'created_by': version_data.get('created_by'),
            'effective_from': version_data.get('effective_from'),
            'effective_to': version_data.get('effective_to')
        })
    
    # Sort by version number descending
    versions.sort(key=lambda v: v.get('version_number', 0), reverse=True)
    
    return {
        "success": True,
        "data": versions
    }


@router.get("/versions/{version_id}", tags=["Version Management"])
def get_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get version details"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == version_id,
        WorkflowTemplate.template_type == 'rule_version'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return {
        "success": True,
        "data": template.definition.get('version', {})
    }


@router.post("/versions/{version_id}/activate", tags=["Version Management"])
def activate_version(
    version_id: str,
    effective_from: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Activate a version"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.version_manager import version_manager
    from backend.services.rules.rule_models import RuleVersion
    
    # Get version
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == version_id,
        WorkflowTemplate.template_type == 'rule_version'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Version not found")
    
    version_data = template.definition.get('version', {})
    version = RuleVersion(**version_data)
    
    # Activate version
    try:
        activated_version = version_manager.activate_version(
            version=version,
            effective_from=effective_from,
            user_id=current_user['id']
        )
        
        # Update version in database
        template.definition = {'version': activated_version.dict()}
        db.commit()
        
        return {
            "success": True,
            "data": activated_version.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/versions/compare", tags=["Version Management"])
def compare_versions(
    version1_id: str,
    version2_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Compare two versions"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.version_manager import version_manager
    from backend.services.rules.rule_models import RuleVersion
    
    # Get both versions
    template1 = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == version1_id,
        WorkflowTemplate.template_type == 'rule_version'
    ).first()
    
    template2 = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == version2_id,
        WorkflowTemplate.template_type == 'rule_version'
    ).first()
    
    if not template1:
        raise HTTPException(status_code=404, detail=f"Version {version1_id} not found")
    if not template2:
        raise HTTPException(status_code=404, detail=f"Version {version2_id} not found")
    
    version1 = RuleVersion(**template1.definition.get('version', {}))
    version2 = RuleVersion(**template2.definition.get('version', {}))
    
    # Compare versions
    comparison = version_manager.compare_versions(version1, version2)
    
    return {
        "success": True,
        "data": comparison.dict()
    }


@router.post("/versions/{version_id}/rollback", tags=["Version Management"])
def rollback_version(
    version_id: str,
    rollback_reason: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Rollback to a specific version"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.version_manager import version_manager
    from backend.services.rules.rule_models import RuleVersion
    
    # Get version
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == version_id,
        WorkflowTemplate.template_type == 'rule_version'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Version not found")
    
    version_data = template.definition.get('version', {})
    version = RuleVersion(**version_data)
    
    # Rollback
    try:
        new_version = version_manager.rollback_to_version(
            version=version,
            rollback_reason=rollback_reason,
            user_id=current_user['id']
        )
        
        # Store new version in database
        new_template = WorkflowTemplate(
            tenant_id=tenant_id,
            template_key=new_version.version_id,
            template_name=new_version.version_name,
            template_type='rule_version',
            definition={'version': new_version.dict()},
            is_active=True,
            created_by=current_user['id']
        )
        
        db.add(new_template)
        db.commit()
        
        return {
            "success": True,
            "data": new_version.dict(),
            "message": f"Rolled back to version {version.version_number}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/versions/{version_id}/archive", tags=["Version Management"])
def archive_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Archive a version"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.version_manager import version_manager
    from backend.services.rules.rule_models import RuleVersion
    
    # Get version
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == version_id,
        WorkflowTemplate.template_type == 'rule_version'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Version not found")
    
    version_data = template.definition.get('version', {})
    version = RuleVersion(**version_data)
    
    # Archive version
    archived_version = version_manager.archive_version(version)
    
    # Update version in database
    template.definition = {'version': archived_version.dict()}
    db.commit()
    
    return {
        "success": True,
        "data": archived_version.dict(),
        "message": "Version archived successfully"
    }


@router.get("/versions/{version_id}/history", tags=["Version Management"])
def get_version_history(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get version history (audit trail)"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    # Get version
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == version_id,
        WorkflowTemplate.template_type == 'rule_version'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Version not found")
    
    version_data = template.definition.get('version', {})
    
    # Get audit trails for this version
    audit_query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'audit_trail'
    )
    
    audit_templates = audit_query.all()
    
    # Filter audit trails for this version
    audit_trails = []
    for audit_template in audit_templates:
        audit_data = audit_template.definition.get('audit', {})
        if audit_data.get('version_id') == version_id:
            audit_trails.append(audit_data)
    
    # Sort by timestamp descending
    audit_trails.sort(key=lambda a: a.get('timestamp', ''), reverse=True)
    
    return {
        "success": True,
        "data": {
            "version": version_data,
            "audit_trail": audit_trails
        }
    }



# ==================== RULE TESTING ====================

@router.post("/test-cases", tags=["Rule Testing"])
def create_test_case(
    test_case_name: str,
    ruleset_id: str,
    input_data: dict,
    expected_output: Optional[dict] = None,
    assertions: Optional[List[dict]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create a test case"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.test_engine import test_engine
    
    # Create test case
    test_case = test_engine.create_test_case(
        test_case_name=test_case_name,
        ruleset_id=ruleset_id,
        input_data=input_data,
        expected_output=expected_output,
        assertions=assertions,
        user_id=current_user['id']
    )
    
    # Store test case in database
    template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=test_case.test_case_id,
        template_name=test_case_name,
        template_type='rule_test_case',
        definition={'test_case': test_case.dict()},
        is_active=True,
        created_by=current_user['id']
    )
    
    db.add(template)
    db.commit()
    
    return {
        "success": True,
        "data": test_case.dict()
    }


@router.get("/test-cases", tags=["Rule Testing"])
def list_test_cases(
    ruleset_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List all test cases"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'rule_test_case'
    )
    
    templates = query.all()
    
    # Filter by ruleset_id if specified
    test_cases = []
    for template in templates:
        test_case_data = template.definition.get('test_case', {})
        
        if ruleset_id and test_case_data.get('ruleset_id') != ruleset_id:
            continue
        
        test_cases.append({
            'test_case_id': template.template_key,
            'test_case_name': test_case_data.get('test_case_name'),
            'ruleset_id': test_case_data.get('ruleset_id'),
            'has_expected_output': test_case_data.get('expected_output') is not None,
            'assertion_count': len(test_case_data.get('assertions', [])),
            'created_at': test_case_data.get('created_at'),
            'created_by': test_case_data.get('created_by')
        })
    
    return {
        "success": True,
        "data": test_cases
    }


@router.get("/test-cases/{test_case_id}", tags=["Rule Testing"])
def get_test_case(
    test_case_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get test case details"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == test_case_id,
        WorkflowTemplate.template_type == 'rule_test_case'
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    return {
        "success": True,
        "data": template.definition.get('test_case', {})
    }


@router.post("/test/dry-run", tags=["Rule Testing"])
def execute_dry_run(
    ruleset_id: str,
    test_case_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Execute test in dry-run mode"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.test_engine import test_engine
    from backend.services.rules.rule_models import RuleSet, RuleTestCase
    
    # Get ruleset
    ruleset_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not ruleset_template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset = RuleSet(**ruleset_template.definition.get('ruleset', {}))
    
    # Get test case
    test_case_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == test_case_id,
        WorkflowTemplate.template_type == 'rule_test_case'
    ).first()
    
    if not test_case_template:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    test_case = RuleTestCase(**test_case_template.definition.get('test_case', {}))
    
    # Execute dry run
    result = test_engine.execute_dry_run(
        ruleset=ruleset,
        test_case=test_case,
        user_id=current_user['id']
    )
    
    # Store test result in database
    result_template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=result.test_result_id,
        template_name=f"Test Result - {test_case.test_case_name}",
        template_type='rule_test_result',
        definition={'result': result.dict()},
        is_active=True,
        created_by=current_user['id']
    )
    
    db.add(result_template)
    db.commit()
    
    return {
        "success": True,
        "data": result.dict()
    }


@router.post("/test/what-if", tags=["Rule Testing"])
def execute_what_if(
    ruleset_id: str,
    input_data: dict,
    modifications: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Execute what-if analysis"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.test_engine import test_engine
    from backend.services.rules.rule_models import RuleSet
    
    # Get ruleset
    ruleset_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not ruleset_template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset = RuleSet(**ruleset_template.definition.get('ruleset', {}))
    
    # Execute what-if analysis
    result = test_engine.execute_what_if(
        ruleset=ruleset,
        input_data=input_data,
        modifications=modifications,
        user_id=current_user['id']
    )
    
    return {
        "success": True,
        "data": result
    }


@router.post("/test/impact-assessment", tags=["Rule Testing"])
def execute_impact_assessment(
    current_ruleset_id: str,
    new_ruleset_id: str,
    sample_data: List[dict],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Execute impact assessment"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.test_engine import test_engine
    from backend.services.rules.rule_models import RuleSet
    
    # Get current ruleset
    current_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == current_ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not current_template:
        raise HTTPException(status_code=404, detail="Current ruleset not found")
    
    current_ruleset = RuleSet(**current_template.definition.get('ruleset', {}))
    
    # Get new ruleset
    new_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == new_ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not new_template:
        raise HTTPException(status_code=404, detail="New ruleset not found")
    
    new_ruleset = RuleSet(**new_template.definition.get('ruleset', {}))
    
    # Execute impact assessment
    assessment = test_engine.execute_impact_assessment(
        current_ruleset=current_ruleset,
        new_ruleset=new_ruleset,
        sample_data=sample_data,
        user_id=current_user['id']
    )
    
    # Store assessment in database
    assessment_template = WorkflowTemplate(
        tenant_id=tenant_id,
        template_key=assessment.assessment_id,
        template_name=f"Impact Assessment - {new_ruleset.ruleset_name}",
        template_type='impact_assessment',
        definition={'assessment': assessment.dict()},
        is_active=True,
        created_by=current_user['id']
    )
    
    db.add(assessment_template)
    db.commit()
    
    return {
        "success": True,
        "data": assessment.dict()
    }


@router.post("/test/batch", tags=["Rule Testing"])
def execute_batch_test(
    ruleset_id: str,
    test_case_ids: List[str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Execute multiple test cases"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.test_engine import test_engine
    from backend.services.rules.rule_models import RuleSet, RuleTestCase
    
    # Get ruleset
    ruleset_template = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_key == ruleset_id,
        WorkflowTemplate.template_type == 'ruleset'
    ).first()
    
    if not ruleset_template:
        raise HTTPException(status_code=404, detail="Ruleset not found")
    
    ruleset = RuleSet(**ruleset_template.definition.get('ruleset', {}))
    
    # Get test cases
    test_cases = []
    for test_case_id in test_case_ids:
        test_case_template = db.query(WorkflowTemplate).filter(
            WorkflowTemplate.tenant_id == tenant_id,
            WorkflowTemplate.template_key == test_case_id,
            WorkflowTemplate.template_type == 'rule_test_case'
        ).first()
        
        if test_case_template:
            test_case = RuleTestCase(**test_case_template.definition.get('test_case', {}))
            test_cases.append(test_case)
    
    # Execute batch test
    results = test_engine.batch_test(
        ruleset=ruleset,
        test_cases=test_cases,
        user_id=current_user['id']
    )
    
    # Store results in database
    for result in results:
        result_template = WorkflowTemplate(
            tenant_id=tenant_id,
            template_key=result.test_result_id,
            template_name=f"Test Result - {result.test_case_id}",
            template_type='rule_test_result',
            definition={'result': result.dict()},
            is_active=True,
            created_by=current_user['id']
        )
        
        db.add(result_template)
    
    db.commit()
    
    # Calculate summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    
    return {
        "success": True,
        "data": {
            "results": [r.dict() for r in results],
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": (passed / total * 100) if total > 0 else 0
            }
        }
    }


@router.get("/test-results", tags=["Rule Testing"])
def list_test_results(
    ruleset_id: Optional[str] = None,
    test_case_id: Optional[str] = None,
    passed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """List test results with filtering"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    
    query = db.query(WorkflowTemplate).filter(
        WorkflowTemplate.tenant_id == tenant_id,
        WorkflowTemplate.template_type == 'rule_test_result'
    )
    
    templates = query.all()
    
    # Filter results
    test_results = []
    for template in templates:
        result_data = template.definition.get('result', {})
        
        if ruleset_id and result_data.get('ruleset_id') != ruleset_id:
            continue
        if test_case_id and result_data.get('test_case_id') != test_case_id:
            continue
        if passed is not None and result_data.get('passed') != passed:
            continue
        
        test_results.append({
            'test_result_id': template.template_key,
            'test_case_id': result_data.get('test_case_id'),
            'ruleset_id': result_data.get('ruleset_id'),
            'execution_mode': result_data.get('execution_mode'),
            'passed': result_data.get('passed'),
            'assertions_passed': result_data.get('assertions_passed'),
            'assertions_failed': result_data.get('assertions_failed'),
            'execution_time_ms': result_data.get('execution_time_ms'),
            'executed_at': result_data.get('executed_at')
        })
    
    return {
        "success": True,
        "data": test_results
    }



# ==================== RULE LIBRARY ====================

@router.get("/library/templates", tags=["Rule Library"])
def get_library_templates(
    category: Optional[str] = None,
    tags: Optional[str] = None
):
    """Get all templates from rule library"""
    from backend.services.rules.rule_library import rule_library
    
    tag_list = tags.split(',') if tags else None
    templates = rule_library.get_all_templates(category=category, tags=tag_list)
    
    return {
        "success": True,
        "data": [t.dict() for t in templates]
    }


@router.get("/library/templates/{template_id}", tags=["Rule Library"])
def get_library_template(
    template_id: str
):
    """Get specific template from library"""
    from backend.services.rules.rule_library import rule_library
    
    template = rule_library.get_template(template_id)
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "success": True,
        "data": template.dict()
    }


@router.get("/library/search", tags=["Rule Library"])
def search_library_templates(
    query: str,
    categories: Optional[str] = None
):
    """Search templates in library"""
    from backend.services.rules.rule_library import rule_library
    
    category_list = categories.split(',') if categories else None
    templates = rule_library.search_templates(query, category_list)
    
    return {
        "success": True,
        "data": [t.dict() for t in templates]
    }


@router.post("/library/templates/{template_id}/clone", tags=["Rule Library"])
def clone_library_template(
    template_id: str,
    new_name: str,
    modifications: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Clone a template from library"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.rule_library import rule_library
    
    try:
        clone = rule_library.clone_template(
            template_id=template_id,
            new_name=new_name,
            modifications=modifications,
            user_id=current_user['id']
        )
        
        # Store clone record in database
        clone_template = WorkflowTemplate(
            tenant_id=tenant_id,
            template_key=clone.clone_id,
            template_name=new_name,
            template_type='rule_clone',
            definition={'clone': clone.dict()},
            is_active=True,
            created_by=current_user['id']
        )
        
        db.add(clone_template)
        db.commit()
        
        return {
            "success": True,
            "data": clone.dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/library/templates/{template_id}/create-ruleset", tags=["Rule Library"])
def create_ruleset_from_template(
    template_id: str,
    ruleset_name: str,
    entity_type: str,
    modifications: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Create a ruleset from library template"""
    from backend.shared.database.workflow_models import WorkflowTemplate
    from backend.services.rules.rule_library import rule_library
    
    try:
        ruleset = rule_library.create_ruleset_from_template(
            template_id=template_id,
            ruleset_name=ruleset_name,
            entity_type=entity_type,
            modifications=modifications,
            user_id=current_user['id']
        )
        
        # Store ruleset in database
        ruleset_template = WorkflowTemplate(
            tenant_id=tenant_id,
            template_key=ruleset.ruleset_id,
            template_name=ruleset_name,
            template_type='ruleset',
            definition={'ruleset': ruleset.dict()},
            is_active=True,
            created_by=current_user['id']
        )
        
        db.add(ruleset_template)
        db.commit()
        
        return {
            "success": True,
            "data": ruleset.dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/library/categories", tags=["Rule Library"])
def get_library_categories():
    """Get all template categories"""
    from backend.services.rules.rule_library import rule_library
    
    categories = rule_library.get_categories()
    
    return {
        "success": True,
        "data": categories
    }


@router.get("/library/compliance-tags", tags=["Rule Library"])
def get_compliance_tags():
    """Get all compliance tags"""
    from backend.services.rules.rule_library import rule_library
    
    tags = rule_library.get_compliance_tags()
    
    return {
        "success": True,
        "data": tags
    }


@router.get("/library/stats", tags=["Rule Library"])
def get_library_stats():
    """Get library statistics"""
    from backend.services.rules.rule_library import rule_library
    
    stats = rule_library.get_template_stats()
    
    # Convert most_used templates to dict
    stats['most_used'] = [t.dict() for t in stats['most_used']]
    
    return {
        "success": True,
        "data": stats
    }
