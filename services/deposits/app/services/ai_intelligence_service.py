"""
AI Intelligence Service
Deposit predictions, behavioral analysis, and recommendations
"""

from decimal import Decimal
from datetime import date, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import uuid
import random


class AIIntelligenceService:
    """
    AI-Powered Deposit Intelligence
    - Renewal predictions
    - Churn risk analysis
    - Product recommendations
    - Customer behavior insights
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def predict_renewal_probability(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """
        Predict likelihood of deposit renewal
        Uses customer history, behavior patterns, and market conditions
        """
        from ..models import DepositAccount, RenewalHistory, DepositIntelligence
        
        account = self.db.query(DepositAccount).filter(
            DepositAccount.id == account_id
        ).first()
        
        if not account:
            raise ValueError(f"Account not found: {account_id}")
        
        # Analyze customer history
        customer_accounts = self.db.query(DepositAccount).filter(
            DepositAccount.customer_id == account.customer_id
        ).all()
        
        total_accounts = len(customer_accounts)
        
        # Check renewal history
        renewals = self.db.query(RenewalHistory).join(
            DepositAccount,
            RenewalHistory.old_account_id == DepositAccount.id
        ).filter(
            DepositAccount.customer_id == account.customer_id
        ).all()
        
        renewal_count = len(renewals)
        
        # Calculate renewal rate
        if total_accounts > 1:
            renewal_rate = (renewal_count / (total_accounts - 1)) * 100
        else:
            renewal_rate = 50  # Default for new customers
        
        # Behavioral factors
        factors = {
            "customer_tenure": self._calculate_customer_tenure(account.customer_id),
            "account_age_days": (date.today() - account.open_date).days,
            "deposit_amount": float(account.principal_amount),
            "interest_rate": float(account.interest_rate),
            "auto_renewal_enabled": account.auto_renewal,
            "previous_renewals": renewal_count,
            "total_accounts": total_accounts
        }
        
        # Simple heuristic model (replace with ML in production)
        probability = self._calculate_renewal_score(factors, renewal_rate)
        
        # Determine recommendation
        if probability >= 75:
            recommendation = "AUTO_RENEW"
            reason = "High confidence in renewal based on customer behavior"
        elif probability >= 50:
            recommendation = "CONTACT_CUSTOMER"
            reason = "Moderate probability - proactive engagement recommended"
        else:
            recommendation = "OFFER_INCENTIVE"
            reason = "Low probability - consider special rate or benefits"
        
        # Save prediction
        intelligence = DepositIntelligence(
            id=uuid.uuid4(),
            customer_id=account.customer_id,
            account_id=account.id,
            analysis_type="RENEWAL_PREDICTION",
            prediction=recommendation,
            confidence_score=Decimal(str(probability)),
            probability=Decimal(str(probability)),
            insights={
                "factors": factors,
                "renewal_rate": renewal_rate
            },
            recommendations=[{
                "action": recommendation,
                "reason": reason
            }],
            data_points_analyzed=len(customer_accounts) + len(renewals),
            model_version="v1.0"
        )
        
        self.db.add(intelligence)
        self.db.commit()
        
        return {
            "account_id": account_id,
            "customer_id": str(account.customer_id),
            "analysis_type": "RENEWAL_PREDICTION",
            "probability": probability,
            "confidence": "HIGH" if probability >= 75 else "MEDIUM" if probability >= 50 else "LOW",
            "recommendation": recommendation,
            "reason": reason,
            "factors_analyzed": factors,
            "maturity_date": account.maturity_date.isoformat()
        }
    
    def analyze_churn_risk(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Analyze customer churn risk
        Identifies customers likely to withdraw deposits
        """
        from ..models import DepositAccount, DepositAccountStatus, PrematureClosure
        
        accounts = self.db.query(DepositAccount).filter(
            DepositAccount.customer_id == customer_id,
            DepositAccount.status.in_([
                DepositAccountStatus.ACTIVE,
                DepositAccountStatus.MATURED
            ])
        ).all()
        
        if not accounts:
            return {
                "customer_id": customer_id,
                "churn_risk": "UNKNOWN",
                "reason": "No active accounts found"
            }
        
        # Check premature closure history
        premature_closures = self.db.query(PrematureClosure).join(
            DepositAccount,
            PrematureClosure.account_id == DepositAccount.id
        ).filter(
            DepositAccount.customer_id == customer_id
        ).count()
        
        total_accounts = len(accounts)
        active_accounts = sum(1 for a in accounts if a.status == DepositAccountStatus.ACTIVE)
        
        # Risk factors
        risk_factors = []
        risk_score = 0
        
        if premature_closures > 0:
            risk_score += 30
            risk_factors.append("Previous premature closures detected")
        
        if active_accounts == 0:
            risk_score += 40
            risk_factors.append("No currently active deposits")
        
        # Check if customer stopped creating new deposits
        latest_account = max(accounts, key=lambda a: a.open_date)
        days_since_last_deposit = (date.today() - latest_account.open_date).days
        
        if days_since_last_deposit > 365:
            risk_score += 20
            risk_factors.append("No new deposits in over 1 year")
        
        # Average deposit amount trend
        avg_amount = sum(a.principal_amount for a in accounts) / len(accounts)
        recent_amounts = [a.principal_amount for a in sorted(accounts, key=lambda x: x.open_date, reverse=True)[:3]]
        
        if recent_amounts and all(amt < avg_amount * Decimal('0.7') for amt in recent_amounts):
            risk_score += 10
            risk_factors.append("Declining deposit amounts")
        
        # Classify risk
        if risk_score >= 60:
            churn_risk = "HIGH"
            actions = [
                "Immediate relationship manager intervention",
                "Offer loyalty bonus or special rates",
                "Personalized retention campaign"
            ]
        elif risk_score >= 30:
            churn_risk = "MEDIUM"
            actions = [
                "Schedule customer review meeting",
                "Present new product options",
                "Check satisfaction and address concerns"
            ]
        else:
            churn_risk = "LOW"
            actions = [
                "Continue regular engagement",
                "Promote premium products"
            ]
        
        return {
            "customer_id": customer_id,
            "churn_risk": churn_risk,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommended_actions": actions,
            "metrics": {
                "total_accounts": total_accounts,
                "active_accounts": active_accounts,
                "premature_closures": premature_closures,
                "days_since_last_deposit": days_since_last_deposit,
                "average_deposit_amount": float(avg_amount)
            }
        }
    
    def recommend_product(
        self,
        customer_id: str,
        amount: Decimal,
        tenure_days: int
    ) -> List[Dict[str, Any]]:
        """
        Recommend best deposit products for customer
        Based on profile, preferences, and goals
        """
        from ..models import DepositProduct, DepositAccount
        from ..engines import RateEngine
        
        # Get customer profile
        customer_accounts = self.db.query(DepositAccount).filter(
            DepositAccount.customer_id == customer_id
        ).all()
        
        # Analyze preferences
        preferred_payout = self._analyze_payout_preference(customer_accounts)
        is_senior_citizen = any(a.is_senior_citizen for a in customer_accounts) if customer_accounts else False
        
        # Get all active products
        products = self.db.query(DepositProduct).filter(
            DepositProduct.status == "ACTIVE",
            DepositProduct.min_amount <= amount
        ).all()
        
        rate_engine = RateEngine(self.db)
        recommendations = []
        
        for product in products:
            try:
                # Calculate rate
                rate_data = rate_engine.calculate_applicable_rate(
                    str(product.id),
                    amount,
                    tenure_days,
                    is_senior_citizen
                )
                
                # Calculate score
                score = self._calculate_product_score(
                    product,
                    rate_data["applicable_rate"],
                    preferred_payout,
                    customer_accounts
                )
                
                recommendations.append({
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "deposit_type": product.deposit_type,
                    "interest_rate": rate_data["applicable_rate"],
                    "payout_frequency": product.payout_frequency,
                    "score": score,
                    "reason": self._generate_recommendation_reason(product, score, preferred_payout)
                })
            except Exception:
                continue
        
        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return recommendations[:5]  # Top 5
    
    def analyze_customer_behavior(
        self,
        customer_id: str
    ) -> Dict[str, Any]:
        """
        Comprehensive customer behavioral analysis
        """
        from ..models import DepositAccount, InterestPosting
        
        accounts = self.db.query(DepositAccount).filter(
            DepositAccount.customer_id == customer_id
        ).all()
        
        if not accounts:
            return {"error": "No accounts found for customer"}
        
        # Behavioral patterns
        patterns = {
            "deposit_frequency": self._calculate_deposit_frequency(accounts),
            "preferred_products": self._find_preferred_products(accounts),
            "average_deposit_amount": float(sum(a.principal_amount for a in accounts) / len(accounts)),
            "preferred_tenure": self._calculate_average_tenure(accounts),
            "interest_sensitivity": self._analyze_interest_sensitivity(accounts),
            "renewal_behavior": self._analyze_renewal_behavior(customer_id),
            "seasonality": self._detect_seasonal_patterns(accounts)
        }
        
        # Insights
        insights = []
        
        if patterns["deposit_frequency"] == "REGULAR":
            insights.append("Customer shows consistent deposit behavior - good retention candidate")
        
        if patterns["interest_sensitivity"] == "HIGH":
            insights.append("Customer responds to rate changes - offer competitive rates")
        
        if patterns["renewal_behavior"]["rate"] > 0.8:
            insights.append("High renewal rate - loyal customer segment")
        
        return {
            "customer_id": customer_id,
            "behavioral_patterns": patterns,
            "insights": insights,
            "segment": self._classify_customer_segment(patterns),
            "lifetime_value": self._estimate_lifetime_value(accounts)
        }
    
    def deposit_copilot(
        self,
        question: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        AI Copilot for deposit queries
        Natural language interface for insights
        """
        question_lower = question.lower()
        
        # Pattern matching (replace with NLP/LLM in production)
        if "maturity" in question_lower and "next" in question_lower:
            return self._answer_maturity_pipeline(context)
        
        elif "renewal" in question_lower:
            return self._answer_renewal_questions(context)
        
        elif "churn" in question_lower or "leaving" in question_lower:
            return self._answer_churn_questions(context)
        
        elif "best" in question_lower and "product" in question_lower:
            return self._answer_product_recommendation(context)
        
        else:
            return {
                "question": question,
                "answer": "I can help you with: maturity pipeline, renewal predictions, churn analysis, and product recommendations. Please rephrase your question.",
                "suggestions": [
                    "Which customers are likely to renew?",
                    "Show me maturities next month",
                    "Identify customers at risk of churning",
                    "What's the best product for a customer?"
                ]
            }
    
    # Helper methods
    
    def _calculate_customer_tenure(self, customer_id: str) -> int:
        """Calculate days since first deposit"""
        from ..models import DepositAccount
        
        first_account = self.db.query(DepositAccount).filter(
            DepositAccount.customer_id == customer_id
        ).order_by(DepositAccount.open_date).first()
        
        if first_account:
            return (date.today() - first_account.open_date).days
        return 0
    
    def _calculate_renewal_score(self, factors: Dict, base_rate: float) -> float:
        """Calculate renewal probability score"""
        score = base_rate
        
        # Adjust based on factors
        if factors["auto_renewal_enabled"]:
            score += 15
        
        if factors["previous_renewals"] > 2:
            score += 10
        
        if factors["customer_tenure"] > 730:  # 2 years
            score += 10
        
        if factors["deposit_amount"] > 100000:
            score += 5
        
        return min(max(score, 0), 100)
    
    def _analyze_payout_preference(self, accounts: List) -> str:
        """Determine customer's preferred payout frequency"""
        if not accounts:
            return "ON_MATURITY"
        
        frequency_count = {}
        for account in accounts:
            freq = account.payout_frequency
            frequency_count[freq] = frequency_count.get(freq, 0) + 1
        
        return max(frequency_count, key=frequency_count.get)
    
    def _calculate_product_score(
        self,
        product: Any,
        rate: float,
        preferred_payout: str,
        customer_accounts: List
    ) -> float:
        """Score product suitability"""
        score = rate * 10  # Base score from interest rate
        
        if product.payout_frequency == preferred_payout:
            score += 20
        
        if product.premature_allowed:
            score += 10
        
        if product.auto_renewal_allowed:
            score += 5
        
        return score
    
    def _generate_recommendation_reason(
        self,
        product: Any,
        score: float,
        preferred_payout: str
    ) -> str:
        """Generate human-readable recommendation reason"""
        reasons = []
        
        if product.payout_frequency == preferred_payout:
            reasons.append("Matches your payout preference")
        
        if score >= 80:
            reasons.append("Best rate available")
        
        if product.premature_allowed:
            reasons.append("Flexible withdrawal options")
        
        return " • ".join(reasons) if reasons else "Good overall fit"
    
    def _calculate_deposit_frequency(self, accounts: List) -> str:
        """Analyze how often customer creates deposits"""
        if len(accounts) < 2:
            return "NEW"
        
        accounts_sorted = sorted(accounts, key=lambda a: a.open_date)
        gaps = []
        
        for i in range(1, len(accounts_sorted)):
            gap = (accounts_sorted[i].open_date - accounts_sorted[i-1].open_date).days
            gaps.append(gap)
        
        avg_gap = sum(gaps) / len(gaps)
        
        if avg_gap < 90:
            return "FREQUENT"
        elif avg_gap < 180:
            return "REGULAR"
        else:
            return "OCCASIONAL"
    
    def _find_preferred_products(self, accounts: List) -> List[str]:
        """Find most used product types"""
        product_count = {}
        
        for account in accounts:
            ptype = account.deposit_type
            product_count[ptype] = product_count.get(ptype, 0) + 1
        
        return sorted(product_count.keys(), key=lambda k: product_count[k], reverse=True)
    
    def _calculate_average_tenure(self, accounts: List) -> int:
        """Average tenure preference in days"""
        if not accounts:
            return 0
        
        tenures = [(a.maturity_date - a.open_date).days for a in accounts]
        return sum(tenures) // len(tenures)
    
    def _analyze_interest_sensitivity(self, accounts: List) -> str:
        """How sensitive customer is to interest rates"""
        if len(accounts) < 3:
            return "UNKNOWN"
        
        rates = [float(a.interest_rate) for a in sorted(accounts, key=lambda x: x.open_date)]
        
        # Check if customer switches products based on rates
        rate_variance = max(rates) - min(rates)
        
        if rate_variance > 1.0:
            return "HIGH"
        elif rate_variance > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _analyze_renewal_behavior(self, customer_id: str) -> Dict[str, Any]:
        """Analyze renewal patterns"""
        from ..models import RenewalHistory, DepositAccount
        
        renewals = self.db.query(RenewalHistory).join(
            DepositAccount,
            RenewalHistory.old_account_id == DepositAccount.id
        ).filter(
            DepositAccount.customer_id == customer_id
        ).all()
        
        total_eligible = self.db.query(DepositAccount).filter(
            DepositAccount.customer_id == customer_id,
            DepositAccount.maturity_date < date.today()
        ).count()
        
        renewal_count = len(renewals)
        
        return {
            "total_eligible": total_eligible,
            "renewed": renewal_count,
            "rate": renewal_count / total_eligible if total_eligible > 0 else 0
        }
    
    def _detect_seasonal_patterns(self, accounts: List) -> Dict[str, Any]:
        """Detect seasonal deposit patterns"""
        months = [a.open_date.month for a in accounts]
        
        month_count = {}
        for month in months:
            month_count[month] = month_count.get(month, 0) + 1
        
        if month_count:
            peak_month = max(month_count, key=month_count.get)
            return {
                "has_pattern": max(month_count.values()) > len(accounts) * 0.3,
                "peak_month": peak_month
            }
        
        return {"has_pattern": False}
    
    def _classify_customer_segment(self, patterns: Dict) -> str:
        """Classify customer into segments"""
        if patterns["average_deposit_amount"] > 500000:
            return "PREMIUM"
        elif patterns["deposit_frequency"] == "FREQUENT":
            return "ACTIVE"
        elif patterns["renewal_behavior"]["rate"] > 0.8:
            return "LOYAL"
        else:
            return "STANDARD"
    
    def _estimate_lifetime_value(self, accounts: List) -> float:
        """Estimate customer lifetime value"""
        total_deposits = sum(float(a.principal_amount) for a in accounts)
        total_interest = sum(float(a.total_interest_earned) for a in accounts)
        
        return total_deposits + total_interest
    
    def _answer_maturity_pipeline(self, context: Dict) -> Dict[str, Any]:
        """Answer maturity-related questions"""
        from ..engines import MaturityEngine
        
        maturity_engine = MaturityEngine(self.db)
        pipeline = maturity_engine.get_maturity_pipeline(days_ahead=30)
        
        total_amount = sum(p["maturity_amount"] for p in pipeline)
        
        return {
            "question": "Maturity pipeline next 30 days",
            "answer": f"You have {len(pipeline)} deposits maturing in the next 30 days with total value of ₹{total_amount:,.2f}",
            "data": {
                "count": len(pipeline),
                "total_amount": total_amount,
                "pipeline": pipeline[:10]
            }
        }
    
    def _answer_renewal_questions(self, context: Dict) -> Dict[str, Any]:
        """Answer renewal-related questions"""
        return {
            "answer": "Use predict_renewal_probability() for specific accounts or check maturity pipeline with renewal flags"
        }
    
    def _answer_churn_questions(self, context: Dict) -> Dict[str, Any]:
        """Answer churn-related questions"""
        return {
            "answer": "Use analyze_churn_risk() for specific customers"
        }
    
    def _answer_product_recommendation(self, context: Dict) -> Dict[str, Any]:
        """Answer product recommendation questions"""
        return {
            "answer": "Use recommend_product() with customer_id, amount, and tenure"
        }
