"""
Eligibility Rules API Router
RESTful API endpoints for eligibility rule management and checking
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from datetime import date

from .eligibility_models import (
    EligibilityRule, EligibilityRuleFilter, EligibilityRuleSummary,
    EligibilityStats, EligibilityRuleClone, RuleStatus,
    EligibilityCheckRequest, EligibilityCheckResponse,
    BulkEligibilityCheckRequest, BulkEligibilityCheckResponse
)
from .eligibility_service import eligibility_service

# Create router
router = APIRouter(prefix="/eligibility-rules", tags=["Eligibility Rules"])


# ============================================================================
# AUTHENTICATION & TENANT HELPERS (Placeholder)
# ============================================================================

async def get_current_user():
    """Get current authenticated user"""
    return {"user_id": "USER001", "tenant_id": "TENANT001"}


async def get_tenant_id(user: dict = Depends(get_current_user)) -> str:
    """Extract tenant ID from current user"""
    return user["tenant_id"]


async def get_user_id(user: dict = Depends(get_current_user)) -> str:
    """Extract user ID from current user"""
    return user["user_id"]


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================

@router.post("/", response_model=EligibilityRule, status_code=status.HTTP_201_CREATED)
async def create_eligibility_rule(
    rule_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Create new eligibility rule
    
    **Parameters:**
    - rule_data: Eligibility rule configuration
    
    **Returns:**
    - Created eligibility rule
    """
    try:
        rule = eligibility_service.create_rule(rule_data, tenant_id, user_id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")


@router.get("/", response_model=List[EligibilityRule])
async def list_eligibility_rules(
    tenant_id: str = Depends(get_tenant_id),
    status: Optional[RuleStatus] = None,
    product_id: Optional[str] = None,
    product_code: Optional[str] = None,
    effective_date_from: Optional[date] = None,
    effective_date_to: Optional[date] = None,
    search_term: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List eligibility rules with filters
    
    **Query Parameters:**
    - status: Filter by rule status
    - product_id: Filter by product ID
    - product_code: Filter by product code
    - effective_date_from: Filter by effective date (from)
    - effective_date_to: Filter by effective date (to)
    - search_term: Search in code, name, description
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    
    **Returns:**
    - List of eligibility rules
    """
    try:
        filters = EligibilityRuleFilter(
            status=status,
            product_id=product_id,
            product_code=product_code,
            effective_date_from=effective_date_from,
            effective_date_to=effective_date_to,
            search_term=search_term
        )
        rules = eligibility_service.list_rules(tenant_id, filters, skip, limit)
        return rules
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list rules: {str(e)}")


@router.get("/{rule_id}", response_model=EligibilityRule)
async def get_eligibility_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get eligibility rule by ID
    
    **Parameters:**
    - rule_id: Rule ID
    
    **Returns:**
    - Eligibility rule details
    """
    try:
        rule = eligibility_service.get_rule(rule_id, tenant_id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rule: {str(e)}")


@router.get("/by-code/{rule_code}", response_model=EligibilityRule)
async def get_eligibility_rule_by_code(
    rule_code: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get eligibility rule by code
    
    **Parameters:**
    - rule_code: Rule code
    
    **Returns:**
    - Eligibility rule details
    """
    try:
        rule = eligibility_service.get_rule_by_code(rule_code, tenant_id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rule: {str(e)}")


@router.put("/{rule_id}", response_model=EligibilityRule)
async def update_eligibility_rule(
    rule_id: str,
    rule_data: dict,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Update eligibility rule
    
    **Parameters:**
    - rule_id: Rule ID
    - rule_data: Updated rule data
    
    **Returns:**
    - Updated eligibility rule
    """
    try:
        rule = eligibility_service.update_rule(rule_id, rule_data, tenant_id, user_id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_eligibility_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Delete eligibility rule
    
    **Parameters:**
    - rule_id: Rule ID
    
    **Returns:**
    - 204 No Content
    """
    try:
        eligibility_service.delete_rule(rule_id, tenant_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {str(e)}")


# ============================================================================
# RULE OPERATIONS
# ============================================================================

@router.post("/{rule_id}/clone", response_model=EligibilityRule, status_code=status.HTTP_201_CREATED)
async def clone_eligibility_rule(
    rule_id: str,
    clone_data: EligibilityRuleClone,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Clone eligibility rule
    
    **Parameters:**
    - rule_id: Rule ID to clone
    - clone_data: Clone configuration (new code, name, product)
    
    **Returns:**
    - Cloned eligibility rule
    """
    try:
        rule = eligibility_service.clone_rule(rule_id, clone_data, tenant_id, user_id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clone rule: {str(e)}")


@router.post("/{rule_id}/activate", response_model=EligibilityRule)
async def activate_eligibility_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Activate eligibility rule
    
    **Parameters:**
    - rule_id: Rule ID
    
    **Returns:**
    - Activated rule
    """
    try:
        rule = eligibility_service.activate_rule(rule_id, tenant_id, user_id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to activate rule: {str(e)}")


@router.post("/{rule_id}/deactivate", response_model=EligibilityRule)
async def deactivate_eligibility_rule(
    rule_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Deactivate eligibility rule
    
    **Parameters:**
    - rule_id: Rule ID
    
    **Returns:**
    - Deactivated rule
    """
    try:
        rule = eligibility_service.deactivate_rule(rule_id, tenant_id, user_id)
        return rule
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deactivate rule: {str(e)}")


# ============================================================================
# ELIGIBILITY CHECKING
# ============================================================================

@router.post("/check", response_model=EligibilityCheckResponse)
async def check_eligibility(
    request: EligibilityCheckRequest,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Check customer eligibility against rule
    
    **Parameters:**
    - request: Eligibility check request with customer data
    
    **Returns:**
    - Detailed eligibility check response
    """
    try:
        response = eligibility_service.check_eligibility(request, tenant_id, user_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check eligibility: {str(e)}")


@router.post("/check/bulk", response_model=BulkEligibilityCheckResponse)
async def bulk_check_eligibility(
    request: BulkEligibilityCheckRequest,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id)
):
    """
    Check eligibility for multiple customers
    
    **Parameters:**
    - request: Bulk eligibility check request
    
    **Returns:**
    - Bulk check results with summary
    """
    try:
        response = eligibility_service.bulk_check_eligibility(request, tenant_id, user_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk check eligibility: {str(e)}")


# ============================================================================
# STATISTICS & UTILITIES
# ============================================================================

@router.get("/stats/summary", response_model=EligibilityStats)
async def get_eligibility_stats(
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Get eligibility rules statistics
    
    **Returns:**
    - Statistics including total rules, checks performed, etc.
    """
    try:
        stats = eligibility_service.get_stats(tenant_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/validation/validate", response_model=dict)
async def validate_rule_data(rule_data: dict):
    """
    Validate eligibility rule data
    
    **Parameters:**
    - rule_data: Rule data to validate
    
    **Returns:**
    - Validation result with errors and warnings
    """
    try:
        validation = eligibility_service.validate_rule_data(rule_data)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate: {str(e)}")


@router.get("/validation/check-code/{rule_code}", response_model=dict)
async def check_rule_code_availability(
    rule_code: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """
    Check if rule code is available
    
    **Parameters:**
    - rule_code: Rule code to check
    
    **Returns:**
    - Availability status and message
    """
    try:
        # Check if code exists
        exists = any(
            r.rule_code == rule_code 
            for r in eligibility_service.rules_storage.values() 
            if r.tenant_id == tenant_id
        )
        
        return {
            "available": not exists,
            "message": f"Rule code '{rule_code}' is {'already in use' if exists else 'available'}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check code: {str(e)}")
