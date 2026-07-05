"""
Business Rules Engine Service Module

This module provides dynamic business rules management and evaluation.

Services:
- Rule Service: Rule and category management
- Evaluation Service: Rule evaluation engine
- Decision Service: Decision management and analytics

Routers:
- Category Router: Categories and rule CRUD
- Evaluation Router: Rule evaluation and testing
- Decision Router: Decision making and analytics

All services follow multi-tenant architecture with complete audit trails.
"""

from .rule_service import RuleService
from .evaluation_service import EvaluationService
from .decision_service import DecisionService
from .category_router import router as category_router
from .evaluation_router import router as evaluation_router
from .decision_router import router as decision_router

__all__ = [
    "RuleService",
    "EvaluationService",
    "DecisionService",
    "category_router",
    "evaluation_router",
    "decision_router",
]
