"""
Decision Engine Service Module

Instant decision-making system for financial products with Rules Engine integration.

Services:
- Decision Service: Core instant decision logic
- Strategy Service: Decision strategy management
- Offer Service: Pre-approved offer management

Router:
- Decision Router: REST API endpoints for decisions, offers, and strategies

Features:
- Instant decisions (< 200ms)
- Rules Engine integration
- Decision caching
- Pre-approved offers
- Confidence scoring
- Complete audit trail
"""

from .decision_service import DecisionService
from .strategy_service import StrategyService
from .offer_service import OfferService
from .router import router

__all__ = [
    "DecisionService",
    "StrategyService",
    "OfferService",
    "router",
]

