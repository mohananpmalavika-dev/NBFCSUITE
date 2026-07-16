"""
Business Rules Engine API Router
FastAPI routes for rules management and execution
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.auth import get_current_user, get_current_tenant
from backend.services.rules.rules_service import RulesService
from backend.services.rules.rules_models import (
    RuleSet, Rule, DecisionTable, DecisionTableRow, RuleExecution, RuleVersion,
    RuleSetCreate, RuleCreate, DecisionTableCreate, DecisionTableRowCreate,
    ExecuteRuleRequest, ExecuteRuleResponse, TestRuleRequest, TestRuleResponse,
    RuleStats, DecisionTableLookupRequest, DecisionTableLookupResponse,
    RuleStatus
)

router = APIRouter(prefix="/api/v1/rules", tags=["Business Rules Engine"])


def get_rules_service(
    db: Session = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant),
    user_id: UUID = Depends(get_current_user)
) -> RulesService:
    """Dependency to get rules service"""
    return RulesService(db, tenant_id, user_id)


# =====================================================================
# RULE SET ENDPOINTS
# =====================================================================

@router.post("/rule-sets/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_rule_set(
    data: RuleSetCreate,
    service: RulesService = Depends(get_rules_service)
):
    """Create a new rule set"""
    try:
        rule_set = service.create_rule_set(data)
        return {
            "id": str(rule_set.id),
            "name": rule_set.name,
            "code": rule_set.code,
            "status": rule_set.status,
            "message": "Rule set created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rule-sets/", response_model=List[dict])
def list_rule_sets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[RuleStatus] = None,
    search: Optional[str] = None,
    service: RulesService = Depends(get_rules_service)
):
    """List rule sets with filters"""
    rule_sets = service.list_rule_sets(skip, limit, category, status, search)
    return [
        {
            "id": str(rs.id),
            "name": rs.name,
            "code": rs.code,
            "description": rs.description,
            "category": rs.category,
            "version": rs.version,
            "status": rs.status,
            "is_active": rs.is_active,
            "execution_mode": rs.execution_mode,
            "priority": rs.priority,
            "rule_count": len(rs.rules),
            "created_at": rs.created_at.isoformat(),
            "updated_at": rs.updated_at.isoformat()
        }
        for rs in rule_sets
    ]



@router.get("/rule-sets/{rule_set_id}", response_model=dict)
def get_rule_set(
    rule_set_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Get rule set by ID"""
    rule_set = service.get_rule_set(rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=404, detail="Rule set not found")
    
    return {
        "id": str(rule_set.id),
        "name": rule_set.name,
        "code": rule_set.code,
        "description": rule_set.description,
        "category": rule_set.category,
        "version": rule_set.version,
        "status": rule_set.status,
        "is_active": rule_set.is_active,
        "execution_mode": rule_set.execution_mode,
        "priority": rule_set.priority,
        "effective_from": rule_set.effective_from.isoformat() if rule_set.effective_from else None,
        "effective_to": rule_set.effective_to.isoformat() if rule_set.effective_to else None,
        "rules": [
            {
                "id": str(r.id),
                "name": r.name,
                "code": r.code,
                "rule_type": r.rule_type,
                "priority": r.priority,
                "is_active": r.is_active,
                "condition_count": len(r.conditions),
                "action_count": len(r.actions)
            }
            for r in rule_set.rules
        ],
        "decision_tables": [
            {
                "id": str(dt.id),
                "name": dt.name,
                "code": dt.code,
                "row_count": len(dt.rows)
            }
            for dt in rule_set.decision_tables
        ],
        "created_at": rule_set.created_at.isoformat(),
        "updated_at": rule_set.updated_at.isoformat()
    }


@router.put("/rule-sets/{rule_set_id}", response_model=dict)
def update_rule_set(
    rule_set_id: UUID,
    data: dict,
    service: RulesService = Depends(get_rules_service)
):
    """Update rule set"""
    rule_set = service.update_rule_set(rule_set_id, data)
    if not rule_set:
        raise HTTPException(status_code=404, detail="Rule set not found")
    
    return {
        "id": str(rule_set.id),
        "name": rule_set.name,
        "message": "Rule set updated successfully"
    }


@router.delete("/rule-sets/{rule_set_id}", response_model=dict)
def delete_rule_set(
    rule_set_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Delete rule set"""
    success = service.delete_rule_set(rule_set_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule set not found")
    return {"message": "Rule set deleted successfully"}


@router.post("/rule-sets/{rule_set_id}/activate", response_model=dict)
def activate_rule_set(
    rule_set_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Activate rule set"""
    rule_set = service.activate_rule_set(rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=404, detail="Rule set not found")
    return {
        "id": str(rule_set.id),
        "is_active": rule_set.is_active,
        "message": "Rule set activated successfully"
    }


@router.post("/rule-sets/{rule_set_id}/deactivate", response_model=dict)
def deactivate_rule_set(
    rule_set_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Deactivate rule set"""
    rule_set = service.deactivate_rule_set(rule_set_id)
    if not rule_set:
        raise HTTPException(status_code=404, detail="Rule set not found")
    return {
        "id": str(rule_set.id),
        "is_active": rule_set.is_active,
        "message": "Rule set deactivated successfully"
    }



# =====================================================================
# RULE ENDPOINTS
# =====================================================================

@router.post("/rule-sets/{rule_set_id}/rules/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_set_id: UUID,
    data: RuleCreate,
    service: RulesService = Depends(get_rules_service)
):
    """Create a new rule"""
    try:
        rule = service.create_rule(rule_set_id, data)
        return {
            "id": str(rule.id),
            "name": rule.name,
            "code": rule.code,
            "message": "Rule created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rules/{rule_id}", response_model=dict)
def get_rule(
    rule_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Get rule by ID"""
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return {
        "id": str(rule.id),
        "rule_set_id": str(rule.rule_set_id),
        "name": rule.name,
        "code": rule.code,
        "description": rule.description,
        "rule_type": rule.rule_type,
        "priority": rule.priority,
        "execution_order": rule.execution_order,
        "logical_operator": rule.logical_operator,
        "stop_on_match": rule.stop_on_match,
        "continue_on_error": rule.continue_on_error,
        "is_active": rule.is_active,
        "tags": rule.tags,
        "conditions": [
            {
                "id": str(c.id),
                "field_name": c.field_name,
                "field_type": c.field_type,
                "operator": c.operator,
                "value": c.value,
                "value_list": c.value_list,
                "logical_operator": c.logical_operator
            }
            for c in rule.conditions
        ],
        "actions": [
            {
                "id": str(a.id),
                "action_type": a.action_type,
                "target_field": a.target_field,
                "value": a.value,
                "expression": a.expression
            }
            for a in rule.actions
        ],
        "created_at": rule.created_at.isoformat(),
        "updated_at": rule.updated_at.isoformat()
    }


@router.put("/rules/{rule_id}", response_model=dict)
def update_rule(
    rule_id: UUID,
    data: dict,
    service: RulesService = Depends(get_rules_service)
):
    """Update rule"""
    rule = service.update_rule(rule_id, data)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"id": str(rule.id), "message": "Rule updated successfully"}


@router.delete("/rules/{rule_id}", response_model=dict)
def delete_rule(
    rule_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Delete rule"""
    success = service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}


@router.post("/rules/{rule_id}/test", response_model=TestRuleResponse)
def test_rule(
    rule_id: UUID,
    request: TestRuleRequest,
    service: RulesService = Depends(get_rules_service)
):
    """Test a rule with sample data"""
    try:
        return service.test_rule(rule_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# =====================================================================
# DECISION TABLE ENDPOINTS
# =====================================================================

@router.post("/rule-sets/{rule_set_id}/decision-tables/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_decision_table(
    rule_set_id: UUID,
    data: DecisionTableCreate,
    service: RulesService = Depends(get_rules_service)
):
    """Create decision table"""
    try:
        table = service.create_decision_table(rule_set_id, data)
        return {
            "id": str(table.id),
            "name": table.name,
            "code": table.code,
            "message": "Decision table created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/decision-tables/{table_id}", response_model=dict)
def get_decision_table(
    table_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Get decision table by ID"""
    table = service.get_decision_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Decision table not found")
    
    return {
        "id": str(table.id),
        "rule_set_id": str(table.rule_set_id),
        "name": table.name,
        "code": table.code,
        "description": table.description,
        "input_columns": table.input_columns,
        "output_columns": table.output_columns,
        "hit_policy": table.hit_policy,
        "is_active": table.is_active,
        "rows": [
            {
                "id": str(r.id),
                "row_number": r.row_number,
                "priority": r.priority,
                "input_values": r.input_values,
                "output_values": r.output_values,
                "description": r.description,
                "is_active": r.is_active
            }
            for r in sorted(table.rows, key=lambda r: r.row_number)
        ],
        "created_at": table.created_at.isoformat(),
        "updated_at": table.updated_at.isoformat()
    }


@router.post("/decision-tables/{table_id}/rows/", response_model=dict, status_code=status.HTTP_201_CREATED)
def add_table_row(
    table_id: UUID,
    data: DecisionTableRowCreate,
    service: RulesService = Depends(get_rules_service)
):
    """Add row to decision table"""
    try:
        row = service.add_table_row(table_id, data)
        return {
            "id": str(row.id),
            "row_number": row.row_number,
            "message": "Row added successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/decision-table-rows/{row_id}", response_model=dict)
def update_table_row(
    row_id: UUID,
    data: dict,
    service: RulesService = Depends(get_rules_service)
):
    """Update decision table row"""
    row = service.update_table_row(row_id, data)
    if not row:
        raise HTTPException(status_code=404, detail="Row not found")
    return {"id": str(row.id), "message": "Row updated successfully"}


@router.delete("/decision-table-rows/{row_id}", response_model=dict)
def delete_table_row(
    row_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """Delete decision table row"""
    success = service.delete_table_row(row_id)
    if not success:
        raise HTTPException(status_code=404, detail="Row not found")
    return {"message": "Row deleted successfully"}


@router.post("/decision-tables/lookup", response_model=DecisionTableLookupResponse)
def lookup_decision_table(
    request: DecisionTableLookupRequest,
    service: RulesService = Depends(get_rules_service)
):
    """Lookup decision table with input values"""
    try:
        return service.lookup_decision_table(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



# =====================================================================
# RULE EXECUTION ENDPOINTS
# =====================================================================

@router.post("/execute", response_model=ExecuteRuleResponse)
def execute_rule_set(
    request: ExecuteRuleRequest,
    service: RulesService = Depends(get_rules_service)
):
    """Execute rule set against input data"""
    try:
        return service.execute_rule_set(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/executions/", response_model=List[dict])
def get_execution_history(
    rule_set_id: Optional[UUID] = None,
    business_key: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    service: RulesService = Depends(get_rules_service)
):
    """Get rule execution history"""
    executions = service.get_rule_execution_history(rule_set_id, business_key, skip, limit)
    return [
        {
            "id": str(ex.id),
            "rule_set_id": str(ex.rule_set_id),
            "execution_context": ex.execution_context,
            "business_key": ex.business_key,
            "rules_evaluated": ex.rules_evaluated,
            "rules_matched": ex.rules_matched,
            "actions_executed": ex.actions_executed,
            "matched_rules": ex.matched_rules,
            "status": ex.status,
            "execution_time_ms": ex.execution_time_ms,
            "started_at": ex.started_at.isoformat(),
            "completed_at": ex.completed_at.isoformat() if ex.completed_at else None
        }
        for ex in executions
    ]


# =====================================================================
# VERSIONING ENDPOINTS
# =====================================================================

@router.post("/rule-sets/{rule_set_id}/versions/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_version(
    rule_set_id: UUID,
    version_name: str,
    description: Optional[str] = None,
    service: RulesService = Depends(get_rules_service)
):
    """Create a version snapshot of rule set"""
    try:
        version = service.create_version(rule_set_id, version_name, description)
        return {
            "id": str(version.id),
            "version_number": version.version_number,
            "version_name": version.version_name,
            "message": "Version created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rule-sets/{rule_set_id}/versions/", response_model=List[dict])
def list_versions(
    rule_set_id: UUID,
    service: RulesService = Depends(get_rules_service)
):
    """List all versions of a rule set"""
    versions = service.list_versions(rule_set_id)
    return [
        {
            "id": str(v.id),
            "version_number": v.version_number,
            "version_name": v.version_name,
            "description": v.description,
            "is_current": v.is_current,
            "created_at": v.created_at.isoformat()
        }
        for v in versions
    ]


# =====================================================================
# ANALYTICS ENDPOINTS
# =====================================================================

@router.get("/stats", response_model=RuleStats)
def get_rule_stats(
    service: RulesService = Depends(get_rules_service)
):
    """Get rule statistics"""
    return service.get_rule_stats()


@router.get("/dashboard", response_model=dict)
def get_dashboard_summary(
    service: RulesService = Depends(get_rules_service)
):
    """Get dashboard summary"""
    stats = service.get_rule_stats()
    recent_executions = service.get_rule_execution_history(limit=10)
    
    return {
        "stats": {
            "total_rule_sets": stats.total_rule_sets,
            "active_rule_sets": stats.active_rule_sets,
            "total_rules": stats.total_rules,
            "total_executions": stats.total_executions,
            "avg_execution_time_ms": stats.avg_execution_time_ms,
            "success_rate": stats.success_rate
        },
        "recent_executions": [
            {
                "id": str(ex.id),
                "execution_context": ex.execution_context,
                "status": ex.status,
                "execution_time_ms": ex.execution_time_ms,
                "created_at": ex.created_at.isoformat()
            }
            for ex in recent_executions
        ]
    }
