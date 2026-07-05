"""
Rule Category & Management Router

API endpoints for rule categories and rule CRUD operations.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.shared.database.connection import get_db
from backend.shared.common.response import success_response
from backend.services.auth.dependencies import get_current_user, get_tenant_id
from .rule_service import RuleService
from .schemas import (
    RuleCategoryCreate,
    RuleCategoryUpdate,
    RuleCategoryResponse,
    BusinessRuleCreate,
    BusinessRuleUpdate,
    BusinessRuleResponse,
    BusinessRuleDetails,
    RuleVersionResponse,
    RuleCloneRequest,
    RuleStatistics,
    RuleType
)

router = APIRouter(prefix="/rules", tags=["Business Rules"])


# ==================== CATEGORY MANAGEMENT ====================

@router.post("/categories", response_model=dict, status_code=201)
def create_category(
    category_data: RuleCategoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create a new rule category
    
    Categories organize rules hierarchically for better management.
    Examples: credit_policy, eligibility, pricing, approval, risk_assessment
    """
    service = RuleService(db, tenant_id, current_user["id"])
    category = service.create_category(category_data)
    
    return success_response(
        message="Category created successfully",
        data=RuleCategoryResponse.from_orm(category).dict()
    )


@router.get("/categories", response_model=dict)
def list_categories(
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List rule categories
    
    Returns hierarchical list of categories for organizing rules.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    categories = service.list_categories(
        parent_id=parent_id,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(categories)} categories",
        data={
            "categories": [RuleCategoryResponse.from_orm(c).dict() for c in categories],
            "total": len(categories),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/categories/{category_id}", response_model=dict)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Get category details"""
    service = RuleService(db, tenant_id, current_user["id"])
    category = service.get_category(category_id)
    
    return success_response(
        message="Category retrieved successfully",
        data=RuleCategoryResponse.from_orm(category).dict()
    )


@router.put("/categories/{category_id}", response_model=dict)
def update_category(
    category_id: int,
    category_data: RuleCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """Update category"""
    service = RuleService(db, tenant_id, current_user["id"])
    category = service.update_category(category_id, category_data)
    
    return success_response(
        message="Category updated successfully",
        data=RuleCategoryResponse.from_orm(category).dict()
    )


@router.delete("/categories/{category_id}", response_model=dict)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Delete category
    
    Only categories without associated rules can be deleted.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    service.delete_category(category_id)
    
    return success_response(
        message="Category deleted successfully",
        data={"category_id": category_id}
    )


# ==================== RULE CRUD ====================

@router.post("", response_model=dict, status_code=201)
def create_rule(
    rule_data: BusinessRuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Create a new business rule
    
    Rules are created in inactive state and must be activated explicitly.
    
    **Rule Definition Structure**:
    - conditions: List of conditions (field, operator, value)
    - logical_operator: AND/OR between conditions
    - actions: Actions to execute when rule matches
    - metadata: Additional rule metadata
    
    **Example**:
    ```json
    {
      "rule_code": "MIN_INCOME_25K",
      "rule_name": "Minimum Income ₹25,000",
      "category_id": 1,
      "rule_type": "eligibility",
      "priority": 100,
      "rule_definition": {
        "conditions": [{
          "field_path": "customer.monthly_income",
          "operator": ">=",
          "value": 25000,
          "data_type": "number"
        }],
        "logical_operator": "AND",
        "actions": [{
          "action_type": "reject",
          "action_config": {
            "message": "Minimum income not met",
            "reason_code": "MIN_INCOME_FAIL"
          }
        }]
      }
    }
    ```
    """
    service = RuleService(db, tenant_id, current_user["id"])
    rule = service.create_rule(rule_data)
    
    return success_response(
        message="Rule created successfully. Activate to make it effective.",
        data=BusinessRuleResponse.from_orm(rule).dict()
    )


@router.get("", response_model=dict)
def list_rules(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    rule_type: Optional[RuleType] = Query(None, description="Filter by type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in code/name/description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    List business rules with filters
    
    Returns rules ordered by priority (lower number = higher priority).
    Only returns rules within their effective date range.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    rules = service.list_rules(
        category_id=category_id,
        rule_type=rule_type.value if rule_type else None,
        is_active=is_active,
        search=search,
        skip=skip,
        limit=limit
    )
    
    return success_response(
        message=f"Retrieved {len(rules)} rules",
        data={
            "rules": [BusinessRuleResponse.from_orm(r).dict() for r in rules],
            "total": len(rules),
            "skip": skip,
            "limit": limit
        }
    )


@router.get("/{rule_id}", response_model=dict)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get rule details
    
    Returns complete rule information including definition, category, and stats.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    rule = service.get_rule(rule_id)
    stats = service.get_rule_stats(rule_id)
    
    return success_response(
        message="Rule retrieved successfully",
        data={
            "rule": BusinessRuleResponse.from_orm(rule).dict(),
            "statistics": stats
        }
    )


@router.put("/{rule_id}", response_model=dict)
def update_rule(
    rule_id: int,
    rule_data: BusinessRuleUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Update rule
    
    **Note**: Cannot modify rule definition while rule is active.
    Deactivate first, then update, then reactivate.
    
    Updates create new version automatically.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    rule = service.update_rule(rule_id, rule_data)
    
    return success_response(
        message="Rule updated successfully",
        data=BusinessRuleResponse.from_orm(rule).dict()
    )


@router.delete("/{rule_id}", response_model=dict)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Delete rule (soft delete)
    
    Only inactive rules can be deleted.
    Deleted rules are retained for audit purposes.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    service.delete_rule(rule_id)
    
    return success_response(
        message="Rule deleted successfully",
        data={"rule_id": rule_id}
    )


# ==================== RULE OPERATIONS ====================

@router.post("/{rule_id}/activate", response_model=dict)
def activate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Activate rule
    
    Makes rule effective for evaluations.
    Rule definition is validated before activation.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    rule = service.activate_rule(rule_id)
    
    return success_response(
        message="Rule activated successfully",
        data=BusinessRuleResponse.from_orm(rule).dict()
    )


@router.post("/{rule_id}/deactivate", response_model=dict)
def deactivate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Deactivate rule
    
    Stops rule from being evaluated.
    Use this to temporarily disable rules without deleting them.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    rule = service.deactivate_rule(rule_id)
    
    return success_response(
        message="Rule deactivated successfully",
        data=BusinessRuleResponse.from_orm(rule).dict()
    )


@router.post("/{rule_id}/clone", response_model=dict)
def clone_rule(
    rule_id: int,
    clone_request: RuleCloneRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Clone rule
    
    Creates a copy of the rule with new code and name.
    Cloned rule starts as inactive.
    
    **Optional**: Copy version history
    """
    service = RuleService(db, tenant_id, current_user["id"])
    cloned_rule = service.clone_rule(
        rule_id=rule_id,
        new_code=clone_request.new_rule_code,
        new_name=clone_request.new_rule_name,
        copy_version_history=clone_request.copy_version_history
    )
    
    return success_response(
        message="Rule cloned successfully",
        data=BusinessRuleResponse.from_orm(cloned_rule).dict()
    )


# ==================== VERSION MANAGEMENT ====================

@router.get("/{rule_id}/versions", response_model=dict)
def get_rule_versions(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get rule version history
    
    Returns complete change history for audit and rollback purposes.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    versions = service.get_rule_versions(rule_id)
    
    return success_response(
        message=f"Retrieved {len(versions)} versions",
        data={
            "rule_id": rule_id,
            "versions": [RuleVersionResponse.from_orm(v).dict() for v in versions],
            "total": len(versions)
        }
    )


@router.post("/{rule_id}/revert/{version_number}", response_model=dict)
def revert_to_version(
    rule_id: int,
    version_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Revert rule to specific version
    
    Restores rule to a previous version.
    Only works for inactive rules.
    Creates a new version entry for the revert action.
    """
    service = RuleService(db, tenant_id, current_user["id"])
    rule = service.revert_to_version(rule_id, version_number)
    
    return success_response(
        message=f"Rule reverted to version {version_number}",
        data=BusinessRuleResponse.from_orm(rule).dict()
    )


# ==================== RULE STATISTICS ====================

@router.get("/{rule_id}/statistics", response_model=dict)
def get_rule_statistics(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    tenant_id: int = Depends(get_tenant_id)
):
    """
    Get rule statistics
    
    Returns:
    - Total evaluations
    - Match count and rate
    - Average execution time
    - Last evaluation timestamp
    """
    service = RuleService(db, tenant_id, current_user["id"])
    stats = service.get_rule_stats(rule_id)
    
    return success_response(
        message="Statistics retrieved successfully",
        data=stats
    )
