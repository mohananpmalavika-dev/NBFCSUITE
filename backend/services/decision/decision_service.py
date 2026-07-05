"""
Decision Service

Core service for making instant decisions, integrating with Rules Engine,
and managing decision lifecycle.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json

from backend.shared.database.decision_models import (
    InstantDecision,
    DecisionStrategy,
    DecisionCache,
    DecisionAnalytics
)
from backend.services.decision.schemas import (
    InstantDecisionRequest,
    InstantDecisionResponse,
    DecisionResult,
    DecisionStatus,
    DecisionFactor
)
from backend.services.rules.evaluation_service import EvaluationService
from backend.services.rules.decision_service import DecisionService as RulesDecisionService


class DecisionService:
    """
    Service for instant decision-making with Rules Engine integration.
    Handles decision requests, caching, and result management.
    """

    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.evaluation_service = EvaluationService(db, tenant_id, user_id)
        self.rules_decision_service = RulesDecisionService(db, tenant_id, user_id)

    async def make_instant_decision(
        self,
        request: InstantDecisionRequest
    ) -> InstantDecisionResponse:
        """
        Make an instant decision based on request and business rules.
        
        Flow:
        1. Check cache if enabled
        2. Load decision strategy
        3. Evaluate rules via Rules Engine
        4. Apply strategy logic
        5. Generate decision
        6. Cache result
        7. Record analytics
        """
        start_time = datetime.utcnow()
        
        # Check cache
        if request.use_cache:
            cached = await self._get_cached_decision(request)
            if cached:
                return cached
        
        # Load strategy
        strategy = await self._get_strategy(
            request.decision_type.value,
            request.strategy_code
        )
        
        if not strategy:
            raise ValueError(f"No active strategy found for {request.decision_type}")
        
        # Prepare input data for rules evaluation
        input_data = await self._prepare_evaluation_data(request)
        
        # Evaluate rules via Rules Engine
        rules_result = await self._evaluate_rules(strategy, request, input_data)
        
        # Apply strategy logic
        decision_result = await self._apply_strategy(strategy, rules_result, request)
        
        # Calculate execution time
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Generate decision number
        decision_number = await self._generate_decision_number()
        
        # Create decision record
        decision = InstantDecision(
            decision_number=decision_number,
            decision_type=request.decision_type.value,
            entity_type=request.request_data.get("entity_type", "loan_application"),
            entity_id=request.request_data.get("entity_id"),
            customer_id=request.customer_id,
            product_id=request.product_id,
            request_data=request.request_data,
            decision_result=decision_result["result"],
            approved_amount=decision_result.get("approved_amount"),
            approved_tenure=decision_result.get("approved_tenure"),
            interest_rate=decision_result.get("interest_rate"),
            processing_fee=decision_result.get("processing_fee"),
            monthly_emi=decision_result.get("monthly_emi"),
            decision_factors=decision_result.get("decision_factors", []),
            rules_applied=decision_result.get("rules_applied", []),
            confidence_score=decision_result.get("confidence_score"),
            decision_reason=decision_result.get("decision_reason"),
            recommendation=decision_result.get("recommendation"),
            rejection_reasons=decision_result.get("rejection_reasons"),
            strategy_used=strategy.strategy_code,
            strategy_id=strategy.id,
            evaluation_time_ms=execution_time,
            cache_hit=False,
            status=DecisionStatus.ACTIVE.value,
            valid_until=datetime.utcnow() + timedelta(
                hours=strategy.strategy_config.get("offer_validity_hours", 72)
            ),
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(decision)
        await self.db.flush()
        await self.db.refresh(decision)
        
        # Cache decision if enabled
        if strategy.strategy_config.get("enable_cache", False):
            await self._cache_decision(request, decision, strategy)
        
        # Record analytics
        await self._record_analytics(decision, strategy)
        
        await self.db.commit()
        
        # Convert to response
        return await self._to_response(decision)

    async def _get_cached_decision(
        self,
        request: InstantDecisionRequest
    ) -> Optional[InstantDecisionResponse]:
        """Check cache for existing decision"""
        cache_key = self._generate_cache_key(request)
        
        query = select(DecisionCache).where(
            and_(
                DecisionCache.cache_key == cache_key,
                DecisionCache.tenant_id == self.tenant_id,
                DecisionCache.expires_at > datetime.utcnow()
            )
        )
        
        result = await self.db.execute(query)
        cache_entry = result.scalar_one_or_none()
        
        if cache_entry:
            # Update hit count
            cache_entry.hit_count += 1
            cache_entry.last_hit_at = datetime.utcnow()
            await self.db.commit()
            
            # Return cached decision with cache_hit flag
            cached_data = cache_entry.cached_decision
            cached_data["cache_hit"] = True
            return InstantDecisionResponse(**cached_data)
        
        return None

    async def _get_strategy(
        self,
        decision_type: str,
        strategy_code: Optional[str] = None
    ) -> Optional[DecisionStrategy]:
        """Get decision strategy (specific or default)"""
        if strategy_code:
            # Get specific strategy
            query = select(DecisionStrategy).where(
                and_(
                    DecisionStrategy.strategy_code == strategy_code,
                    DecisionStrategy.tenant_id == self.tenant_id,
                    DecisionStrategy.is_active == True,
                    DecisionStrategy.is_deleted == False
                )
            )
        else:
            # Get default strategy for decision type
            query = select(DecisionStrategy).where(
                and_(
                    DecisionStrategy.decision_type == decision_type,
                    DecisionStrategy.tenant_id == self.tenant_id,
                    DecisionStrategy.is_active == True,
                    DecisionStrategy.is_deleted == False
                )
            ).order_by(
                DecisionStrategy.is_default.desc(),
                DecisionStrategy.priority.asc()
            ).limit(1)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _prepare_evaluation_data(
        self,
        request: InstantDecisionRequest
    ) -> Dict[str, Any]:
        """Prepare input data for rules evaluation"""
        # Merge request data with customer data
        input_data = request.request_data.copy()
        
        # Add customer ID for rules that check it
        input_data["customer_id"] = request.customer_id
        
        if request.product_id:
            input_data["product_id"] = request.product_id
        
        # TODO: Fetch additional customer data from Customer Module
        # customer = await customer_service.get_customer(request.customer_id)
        # input_data["customer"] = customer.to_dict()
        
        return input_data

    async def _evaluate_rules(
        self,
        strategy: DecisionStrategy,
        request: InstantDecisionRequest,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate business rules via Rules Engine"""
        strategy_config = strategy.strategy_config
        
        # Get rule categories from strategy
        rule_categories = strategy_config.get("rule_categories", [])
        
        if not rule_categories:
            # No rules to evaluate
            return {
                "evaluation_result": "pass",
                "rules_matched": 0,
                "confidence_score": 100.0,
                "decision_factors": []
            }
        
        # Evaluate rules
        try:
            evaluation_result = await self.evaluation_service.evaluate_rules(
                category_codes=rule_categories,
                entity_type=request.request_data.get("entity_type", "loan_application"),
                entity_id=request.request_data.get("entity_id"),
                input_data=input_data,
                evaluation_strategy=strategy_config.get("evaluation_strategy", "all_match")
            )
            
            return {
                "evaluation_result": evaluation_result.get("overall_result", "pass"),
                "rules_matched": evaluation_result.get("rules_matched", 0),
                "rules_evaluated": evaluation_result.get("total_rules_evaluated", 0),
                "confidence_score": evaluation_result.get("confidence_score", 100.0),
                "evaluation_results": evaluation_result.get("evaluation_results", []),
                "execution_time_ms": evaluation_result.get("execution_time_ms", 0)
            }
        except Exception as e:
            # If rules evaluation fails, return error
            return {
                "evaluation_result": "error",
                "error": str(e),
                "confidence_score": 0.0
            }

    async def _apply_strategy(
        self,
        strategy: DecisionStrategy,
        rules_result: Dict[str, Any],
        request: InstantDecisionRequest
    ) -> Dict[str, Any]:
        """Apply strategy logic to determine final decision"""
        confidence_score = Decimal(str(rules_result.get("confidence_score", 0)))
        requested_amount = Decimal(str(request.request_data.get("loan_amount", 0)))
        
        # Get thresholds from strategy
        auto_approve_threshold = strategy.auto_approve_threshold
        manual_review_threshold = strategy.manual_review_threshold
        auto_reject_threshold = strategy.auto_reject_threshold
        max_auto_approve = strategy.max_amount_auto_approve
        
        decision_result = {
            "confidence_score": confidence_score,
            "decision_factors": self._extract_decision_factors(rules_result, request),
            "rules_applied": rules_result.get("evaluation_results", [])
        }
        
        # Check if rules evaluation had errors
        if rules_result.get("evaluation_result") == "error":
            decision_result["result"] = DecisionResult.ERROR.value
            decision_result["decision_reason"] = "Error evaluating business rules"
            decision_result["rejection_reasons"] = [rules_result.get("error", "Unknown error")]
            return decision_result
        
        # Check if any critical rules failed
        if rules_result.get("evaluation_result") == "fail":
            decision_result["result"] = DecisionResult.REJECTED.value
            decision_result["decision_reason"] = "Failed critical eligibility criteria"
            decision_result["rejection_reasons"] = self._extract_rejection_reasons(rules_result)
            return decision_result
        
        # Apply confidence-based decision logic
        if confidence_score >= auto_approve_threshold:
            # High confidence - check amount limit
            if max_auto_approve and requested_amount > max_auto_approve:
                decision_result["result"] = DecisionResult.MANUAL_REVIEW.value
                decision_result["decision_reason"] = f"Amount exceeds auto-approval limit of ₹{max_auto_approve:,.2f}"
                decision_result["recommendation"] = "Manual review required for high-value application"
            else:
                # Auto-approve
                decision_result["result"] = DecisionResult.APPROVED.value
                decision_result["approved_amount"] = requested_amount
                decision_result["approved_tenure"] = request.request_data.get("tenure")
                decision_result["interest_rate"] = await self._calculate_interest_rate(
                    request, confidence_score
                )
                decision_result["processing_fee"] = await self._calculate_processing_fee(
                    requested_amount, request.product_id
                )
                decision_result["monthly_emi"] = await self._calculate_emi(
                    decision_result["approved_amount"],
                    decision_result["interest_rate"],
                    decision_result["approved_tenure"]
                )
                decision_result["decision_reason"] = "All eligibility criteria met with high confidence"
                decision_result["recommendation"] = "Approved for instant disbursement"
        
        elif confidence_score >= manual_review_threshold:
            # Medium confidence - manual review
            decision_result["result"] = DecisionResult.MANUAL_REVIEW.value
            decision_result["decision_reason"] = "Borderline case - requires manual review"
            decision_result["recommendation"] = "Review application with underwriting team"
        
        else:
            # Low confidence or explicit reject threshold
            if auto_reject_threshold and confidence_score < auto_reject_threshold:
                decision_result["result"] = DecisionResult.REJECTED.value
                decision_result["decision_reason"] = "Low confidence score - eligibility criteria not met"
                decision_result["rejection_reasons"] = self._extract_rejection_reasons(rules_result)
            else:
                decision_result["result"] = DecisionResult.MANUAL_REVIEW.value
                decision_result["decision_reason"] = "Low confidence - manual review recommended"
                decision_result["recommendation"] = "Detailed review required"
        
        return decision_result

    def _extract_decision_factors(
        self,
        rules_result: Dict[str, Any],
        request: InstantDecisionRequest
    ) -> List[Dict[str, Any]]:
        """Extract key factors that influenced the decision"""
        factors = []
        
        # Extract from rules evaluation
        evaluation_results = rules_result.get("evaluation_results", [])
        for rule_result in evaluation_results:
            if rule_result.get("matched"):
                factors.append({
                    "factor": rule_result.get("rule_name"),
                    "value": "matched",
                    "impact": "positive",
                    "weight": 0.5
                })
            else:
                factors.append({
                    "factor": rule_result.get("rule_name"),
                    "value": "not_matched",
                    "impact": "negative",
                    "weight": 0.5
                })
        
        # Add request-based factors
        request_data = request.request_data
        if "customer_data" in request_data:
            customer_data = request_data["customer_data"]
            
            # Income factor
            if "monthly_income" in customer_data:
                factors.append({
                    "factor": "Monthly Income",
                    "value": customer_data["monthly_income"],
                    "impact": "positive" if customer_data["monthly_income"] >= 25000 else "negative",
                    "weight": 0.25
                })
            
            # Existing EMI factor
            if "existing_emi" in customer_data:
                factors.append({
                    "factor": "Existing EMI",
                    "value": customer_data["existing_emi"],
                    "impact": "neutral",
                    "weight": 0.15
                })
        
        return factors

    def _extract_rejection_reasons(
        self,
        rules_result: Dict[str, Any]
    ) -> List[str]:
        """Extract rejection reasons from failed rules"""
        reasons = []
        
        evaluation_results = rules_result.get("evaluation_results", [])
        for rule_result in evaluation_results:
            if not rule_result.get("matched") and rule_result.get("evaluation_result") == "fail":
                rule_name = rule_result.get("rule_name", "Unknown rule")
                reasons.append(f"{rule_name} criteria not met")
        
        return reasons if reasons else ["Eligibility criteria not met"]

    async def _calculate_interest_rate(
        self,
        request: InstantDecisionRequest,
        confidence_score: Decimal
    ) -> Decimal:
        """Calculate interest rate based on confidence/risk"""
        # Base rate from product (TODO: fetch from product)
        base_rate = Decimal("12.0")
        
        # Risk-based adjustment
        if confidence_score >= 90:
            adjustment = Decimal("-1.0")  # 1% discount
        elif confidence_score >= 85:
            adjustment = Decimal("-0.5")  # 0.5% discount
        elif confidence_score >= 80:
            adjustment = Decimal("0.0")  # No adjustment
        elif confidence_score >= 75:
            adjustment = Decimal("0.5")  # 0.5% premium
        else:
            adjustment = Decimal("1.0")  # 1% premium
        
        final_rate = base_rate + adjustment
        return max(Decimal("10.0"), min(final_rate, Decimal("24.0")))

    async def _calculate_processing_fee(
        self,
        amount: Decimal,
        product_id: Optional[int]
    ) -> Decimal:
        """Calculate processing fee"""
        # Standard 1% fee (TODO: fetch from product config)
        fee_percentage = Decimal("1.0")
        fee = (amount * fee_percentage) / Decimal("100")
        
        # Min and max fee
        min_fee = Decimal("500")
        max_fee = Decimal("10000")
        
        return max(min_fee, min(fee, max_fee))

    async def _calculate_emi(
        self,
        amount: Decimal,
        rate: Decimal,
        tenure: int
    ) -> Decimal:
        """Calculate monthly EMI"""
        if tenure == 0:
            return Decimal("0")
        
        monthly_rate = rate / Decimal("12") / Decimal("100")
        
        if monthly_rate == 0:
            return amount / Decimal(str(tenure))
        
        # EMI = P * r * (1 + r)^n / ((1 + r)^n - 1)
        power = (1 + float(monthly_rate)) ** tenure
        emi = amount * monthly_rate * Decimal(str(power)) / Decimal(str(power - 1))
        
        return emi.quantize(Decimal("0.01"))

    async def _generate_decision_number(self) -> str:
        """Generate unique decision number"""
        now = datetime.utcnow()
        
        # Format: DEC-YYYYMM-XXXXX
        prefix = f"DEC-{now.strftime('%Y%m')}"
        
        # Get count for this month
        query = select(func.count(InstantDecision.id)).where(
            and_(
                InstantDecision.decision_number.like(f"{prefix}%"),
                InstantDecision.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return f"{prefix}-{count + 1:05d}"

    def _generate_cache_key(self, request: InstantDecisionRequest) -> str:
        """Generate cache key from request"""
        # Create hash from customer_id, decision_type, and key request params
        key_data = {
            "customer_id": request.customer_id,
            "decision_type": request.decision_type.value,
            "product_id": request.product_id,
            "loan_amount": request.request_data.get("loan_amount"),
            "tenure": request.request_data.get("tenure")
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def _cache_decision(
        self,
        request: InstantDecisionRequest,
        decision: InstantDecision,
        strategy: DecisionStrategy
    ):
        """Cache decision result"""
        cache_key = self._generate_cache_key(request)
        ttl_minutes = strategy.strategy_config.get("cache_ttl_minutes", 30)
        
        # Prepare cached data
        cached_data = {
            "decision_id": decision.id,
            "decision_number": decision.decision_number,
            "decision_result": decision.decision_result,
            "approved_amount": float(decision.approved_amount) if decision.approved_amount else None,
            "approved_tenure": decision.approved_tenure,
            "interest_rate": float(decision.interest_rate) if decision.interest_rate else None,
            "processing_fee": float(decision.processing_fee) if decision.processing_fee else None,
            "monthly_emi": float(decision.monthly_emi) if decision.monthly_emi else None,
            "confidence_score": float(decision.confidence_score) if decision.confidence_score else None,
            "decision_reason": decision.decision_reason,
            "recommendation": decision.recommendation,
            "valid_until": decision.valid_until.isoformat() if decision.valid_until else None,
            "evaluation_time_ms": decision.evaluation_time_ms,
            "strategy_used": decision.strategy_used
        }
        
        cache_entry = DecisionCache(
            cache_key=cache_key,
            decision_type=request.decision_type.value,
            customer_id=request.customer_id,
            product_id=request.product_id,
            cached_decision=cached_data,
            ttl_minutes=ttl_minutes,
            expires_at=datetime.utcnow() + timedelta(minutes=ttl_minutes),
            tenant_id=self.tenant_id
        )
        
        self.db.add(cache_entry)

    async def _record_analytics(
        self,
        decision: InstantDecision,
        strategy: DecisionStrategy
    ):
        """Record decision for analytics (would be done in background)"""
        # This would typically be done asynchronously via message queue
        # For now, we'll just log it
        pass

    async def _to_response(
        self,
        decision: InstantDecision
    ) -> InstantDecisionResponse:
        """Convert decision model to response schema"""
        return InstantDecisionResponse(
            decision_id=decision.id,
            decision_number=decision.decision_number,
            decision_result=DecisionResult(decision.decision_result),
            approved_amount=decision.approved_amount,
            approved_tenure=decision.approved_tenure,
            interest_rate=decision.interest_rate,
            processing_fee=decision.processing_fee,
            monthly_emi=decision.monthly_emi,
            confidence_score=decision.confidence_score,
            decision_reason=decision.decision_reason,
            recommendation=decision.recommendation,
            rejection_reasons=decision.rejection_reasons,
            decision_factors=[DecisionFactor(**f) for f in (decision.decision_factors or [])],
            rules_applied=decision.rules_applied,
            valid_until=decision.valid_until,
            evaluation_time_ms=decision.evaluation_time_ms,
            cache_hit=decision.cache_hit,
            strategy_used=decision.strategy_used
        )

    async def get_decision(self, decision_id: int) -> Optional[InstantDecision]:
        """Get decision by ID"""
        query = select(InstantDecision).where(
            and_(
                InstantDecision.id == decision_id,
                InstantDecision.tenant_id == self.tenant_id,
                InstantDecision.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def accept_decision(
        self,
        decision_id: int,
        remarks: Optional[str] = None
    ) -> InstantDecision:
        """Mark decision as accepted by customer"""
        decision = await self.get_decision(decision_id)
        
        if not decision:
            raise ValueError("Decision not found")
        
        if decision.status != DecisionStatus.ACTIVE.value:
            raise ValueError(f"Decision is {decision.status}, cannot accept")
        
        if decision.valid_until and decision.valid_until < datetime.utcnow():
            raise ValueError("Decision has expired")
        
        decision.status = DecisionStatus.ACCEPTED.value
        decision.accepted_at = datetime.utcnow()
        decision.accepted_by = self.user_id
        decision.updated_by = self.user_id
        decision.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(decision)
        
        return decision

    async def reject_decision(
        self,
        decision_id: int,
        reason: str
    ) -> InstantDecision:
        """Mark decision as rejected by customer"""
        decision = await self.get_decision(decision_id)
        
        if not decision:
            raise ValueError("Decision not found")
        
        decision.status = DecisionStatus.REJECTED_BY_CUSTOMER.value
        decision.rejected_at = datetime.utcnow()
        decision.rejection_reason = reason
        decision.updated_by = self.user_id
        decision.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(decision)
        
        return decision

    async def get_customer_decisions(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[InstantDecision]:
        """Get recent decisions for a customer"""
        query = select(InstantDecision).where(
            and_(
                InstantDecision.customer_id == customer_id,
                InstantDecision.tenant_id == self.tenant_id,
                InstantDecision.is_deleted == False
            )
        ).order_by(
            InstantDecision.created_at.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

