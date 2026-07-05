"""
Decision Service

Manages decision-making based on rule evaluations including:
- Decision creation and logging
- Decision override management
- Decision analytics
- Confidence scoring
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from backend.shared.database.rules_models import RuleDecision, RuleEvaluation
from backend.shared.common.response import CustomException
from .schemas import DecisionRequest, DecisionResult, DecisionOverrideRequest
from .evaluation_service import EvaluationService


class DecisionService:
    """Service for managing rule-based decisions"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.evaluation_service = EvaluationService(db, tenant_id, user_id)
    
    # ==================== DECISION MAKING ====================
    
    def make_decision(self, request: DecisionRequest) -> Dict[str, Any]:
        """
        Make a decision by evaluating multiple rules
        
        Args:
            request: Decision request with input data
            
        Returns:
            Decision with result, factors, and recommendation
        """
        # Build evaluation request
        from .schemas import EvaluationRequest
        
        eval_request = EvaluationRequest(
            category_code=request.category_codes[0] if request.category_codes else None,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            input_data=request.input_data
        )
        
        # Evaluate rules
        evaluation_result = self.evaluation_service.evaluate_rules(eval_request)
        
        # Analyze results and make decision
        decision_result = self._analyze_evaluation_results(evaluation_result)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(evaluation_result)
        
        # Extract decision factors
        decision_factors = self._extract_decision_factors(evaluation_result)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            decision_result,
            decision_factors,
            evaluation_result
        )
        
        # Create decision record
        decision = RuleDecision(
            decision_id=uuid.uuid4(),
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            decision_type=request.decision_type,
            decision_result=decision_result.value,
            confidence_score=confidence_score,
            rules_applied=self._format_rules_applied(evaluation_result),
            decision_factors=decision_factors,
            recommendation=recommendation,
            override_applied=False,
            tenant_id=self.tenant_id,
            decided_by=self.user_id
        )
        
        self.db.add(decision)
        self.db.commit()
        self.db.refresh(decision)
        
        return {
            "decision_id": decision.decision_id,
            "entity_type": decision.entity_type,
            "entity_id": decision.entity_id,
            "decision_type": decision.decision_type,
            "decision_result": decision.decision_result,
            "confidence_score": float(decision.confidence_score) if decision.confidence_score else None,
            "rules_applied": decision.rules_applied,
            "decision_factors": decision.decision_factors,
            "recommendation": decision.recommendation,
            "decided_at": decision.decided_at
        }
    
    def _analyze_evaluation_results(self, evaluation_result: Dict[str, Any]) -> DecisionResult:
        """Analyze evaluation results to determine final decision"""
        overall_result = evaluation_result.get('overall_result')
        evaluation_results = evaluation_result.get('evaluation_results', [])
        
        # Count different result types
        reject_count = 0
        approve_count = 0
        manual_review_count = 0
        error_count = 0
        
        for result in evaluation_results:
            if not result['matched']:
                continue
            
            # Check action types in output_data
            output_data = result.get('output_data', {})
            actions = output_data.get('actions', [])
            
            for action in actions:
                action_type = action.get('action_type')
                if action_type == 'reject':
                    reject_count += 1
                elif action_type == 'approve':
                    approve_count += 1
                elif action_type == 'manual_review':
                    manual_review_count += 1
        
        # Decision logic
        if overall_result == 'error':
            return DecisionResult.ERROR
        
        # Any rejection means reject
        if reject_count > 0:
            return DecisionResult.REJECTED
        
        # If manual review required
        if manual_review_count > 0:
            return DecisionResult.MANUAL_REVIEW
        
        # If approvals exist and no rejections
        if approve_count > 0:
            return DecisionResult.APPROVED
        
        # No explicit decision - default to manual review
        return DecisionResult.MANUAL_REVIEW
    
    def _calculate_confidence(self, evaluation_result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for the decision
        
        Based on:
        - Number of rules evaluated
        - Consistency of results
        - Rule priorities
        """
        results = evaluation_result.get('evaluation_results', [])
        
        if not results:
            return 0.0
        
        # Base confidence on consistency
        matched_count = sum(1 for r in results if r['matched'])
        total_count = len(results)
        
        # If all rules agree (all pass or all fail), high confidence
        if matched_count == 0 or matched_count == total_count:
            confidence = 95.0
        else:
            # Mixed results - lower confidence
            match_ratio = matched_count / total_count
            confidence = 50.0 + (abs(0.5 - match_ratio) * 90.0)
        
        # Reduce confidence if errors occurred
        error_count = sum(1 for r in results if r['evaluation_result'] == 'error')
        if error_count > 0:
            confidence *= (1 - (error_count / total_count) * 0.5)
        
        return round(confidence, 2)
    
    def _extract_decision_factors(
        self,
        evaluation_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract key factors that influenced the decision"""
        factors = []
        results = evaluation_result.get('evaluation_results', [])
        
        for result in results:
            if result['matched']:
                # This rule contributed to the decision
                output_data = result.get('output_data', {})
                actions = output_data.get('actions', [])
                
                for action in actions:
                    action_type = action.get('action_type')
                    config = action.get('config', {})
                    
                    factor = {
                        "factor_name": result['rule_name'],
                        "factor_value": action_type,
                        "impact": self._get_action_impact(action_type),
                        "weight": self._get_action_weight(action_type),
                        "message": config.get('message', ''),
                        "reason_code": config.get('reason_code', '')
                    }
                    
                    factors.append(factor)
        
        return factors
    
    def _get_action_impact(self, action_type: str) -> str:
        """Determine impact of an action"""
        if action_type in ['approve', 'set_value']:
            return 'positive'
        elif action_type in ['reject', 'fail']:
            return 'negative'
        else:
            return 'neutral'
    
    def _get_action_weight(self, action_type: str) -> float:
        """Determine weight of an action"""
        weights = {
            'reject': 1.0,
            'approve': 0.9,
            'manual_review': 0.7,
            'set_value': 0.5,
            'log_event': 0.1
        }
        return weights.get(action_type, 0.5)
    
    def _generate_recommendation(
        self,
        decision_result: DecisionResult,
        decision_factors: List[Dict[str, Any]],
        evaluation_result: Dict[str, Any]
    ) -> str:
        """Generate human-readable recommendation"""
        if decision_result == DecisionResult.APPROVED:
            return "All eligibility criteria met. Recommend approval."
        
        elif decision_result == DecisionResult.REJECTED:
            # List rejection reasons
            reasons = [
                f["message"] for f in decision_factors 
                if f["impact"] == "negative" and f.get("message")
            ]
            if reasons:
                return f"Rejected due to: {'; '.join(reasons)}"
            return "Does not meet eligibility criteria. Recommend rejection."
        
        elif decision_result == DecisionResult.MANUAL_REVIEW:
            return "Requires manual review. Mixed or insufficient automated decision criteria."
        
        elif decision_result == DecisionResult.ERROR:
            return "Error occurred during evaluation. Manual intervention required."
        
        return "Decision pending further review."
    
    def _format_rules_applied(self, evaluation_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format rules applied for storage"""
        results = evaluation_result.get('evaluation_results', [])
        
        return [
            {
                "rule_id": r['rule_id'],
                "rule_code": r['rule_code'],
                "matched": r['matched'],
                "result": r['evaluation_result']
            }
            for r in results
        ]
    
    # ==================== DECISION RETRIEVAL ====================
    
    def get_decision(self, decision_id: uuid.UUID) -> Optional[RuleDecision]:
        """Get decision by ID"""
        return self.db.query(RuleDecision).filter(
            and_(
                RuleDecision.decision_id == decision_id,
                RuleDecision.tenant_id == self.tenant_id
            )
        ).first()
    
    def get_entity_decisions(
        self,
        entity_type: str,
        entity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[RuleDecision]:
        """Get all decisions for an entity"""
        return self.db.query(RuleDecision).filter(
            and_(
                RuleDecision.entity_type == entity_type,
                RuleDecision.entity_id == entity_id,
                RuleDecision.tenant_id == self.tenant_id
            )
        ).order_by(
            RuleDecision.decided_at.desc()
        ).offset(skip).limit(limit).all()
    
    def list_decisions(
        self,
        decision_type: Optional[str] = None,
        decision_result: Optional[DecisionResult] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RuleDecision]:
        """List decisions with filters"""
        query = self.db.query(RuleDecision).filter(
            RuleDecision.tenant_id == self.tenant_id
        )
        
        if decision_type:
            query = query.filter(RuleDecision.decision_type == decision_type)
        
        if decision_result:
            query = query.filter(RuleDecision.decision_result == decision_result.value)
        
        query = query.order_by(RuleDecision.decided_at.desc())
        
        return query.offset(skip).limit(limit).all()
    
    # ==================== DECISION OVERRIDE ====================
    
    def override_decision(
        self,
        decision_id: uuid.UUID,
        override_request: DecisionOverrideRequest
    ) -> RuleDecision:
        """Override a decision"""
        decision = self.get_decision(decision_id)
        
        if not decision:
            raise CustomException(status_code=404, message="Decision not found")
        
        if decision.override_applied:
            raise CustomException(
                status_code=400,
                message="Decision has already been overridden"
            )
        
        # Apply override
        decision.override_applied = True
        decision.override_by = self.user_id
        decision.override_reason = override_request.reason
        decision.override_at = datetime.utcnow()
        decision.decision_result = override_request.new_result.value
        
        self.db.commit()
        self.db.refresh(decision)
        
        return decision
    
    # ==================== DECISION ANALYTICS ====================
    
    def get_decision_statistics(
        self,
        decision_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get decision statistics"""
        query = self.db.query(RuleDecision).filter(
            RuleDecision.tenant_id == self.tenant_id
        )
        
        if decision_type:
            query = query.filter(RuleDecision.decision_type == decision_type)
        
        # Total decisions
        total = query.count()
        
        # Count by result
        approved = query.filter(
            RuleDecision.decision_result == DecisionResult.APPROVED.value
        ).count()
        
        rejected = query.filter(
            RuleDecision.decision_result == DecisionResult.REJECTED.value
        ).count()
        
        manual_review = query.filter(
            RuleDecision.decision_result == DecisionResult.MANUAL_REVIEW.value
        ).count()
        
        # Average confidence
        avg_confidence = query.with_entities(
            func.avg(RuleDecision.confidence_score)
        ).scalar() or 0
        
        # Override rate
        overridden = query.filter(
            RuleDecision.override_applied == True
        ).count()
        
        return {
            "decision_type": decision_type or "all",
            "total_decisions": total,
            "approved": approved,
            "rejected": rejected,
            "manual_review": manual_review,
            "pending": 0,  # Not tracked separately
            "error": 0,  # Not tracked separately
            "approval_rate": (approved / total * 100) if total > 0 else 0,
            "rejection_rate": (rejected / total * 100) if total > 0 else 0,
            "manual_review_rate": (manual_review / total * 100) if total > 0 else 0,
            "avg_confidence_score": float(avg_confidence),
            "override_count": overridden,
            "override_rate": (overridden / total * 100) if total > 0 else 0
        }
    
    def get_decision_trends(
        self,
        decision_type: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get decision trends over time"""
        from datetime import timedelta
        from sqlalchemy import Date, cast
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = self.db.query(
            cast(RuleDecision.decided_at, Date).label('date'),
            RuleDecision.decision_result,
            func.count(RuleDecision.id).label('count')
        ).filter(
            and_(
                RuleDecision.tenant_id == self.tenant_id,
                RuleDecision.decided_at >= start_date
            )
        )
        
        if decision_type:
            query = query.filter(RuleDecision.decision_type == decision_type)
        
        query = query.group_by(
            cast(RuleDecision.decided_at, Date),
            RuleDecision.decision_result
        ).order_by(
            cast(RuleDecision.decided_at, Date)
        )
        
        results = query.all()
        
        # Format results
        trends = {}
        for date, result, count in results:
            date_str = date.isoformat()
            if date_str not in trends:
                trends[date_str] = {
                    "date": date_str,
                    "approved": 0,
                    "rejected": 0,
                    "manual_review": 0,
                    "total": 0
                }
            
            trends[date_str][result.lower().replace('_', '_')] = count
            trends[date_str]["total"] += count
        
        return list(trends.values())
