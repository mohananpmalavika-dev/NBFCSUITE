"""
Transaction Monitoring Service for AML/CFT
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from backend.shared.database.aml_models import (
    AMLTransactionMonitoring,
    AMLMonitoringRule,
    TransactionRiskLevel
)
from backend.services.aml.schemas import (
    TransactionMonitoringCreate,
    TransactionMonitoringFilter
)
from backend.services.aml.alert_service import AMLAlertService


class TransactionMonitoringService:
    """Service for transaction monitoring"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.alert_service = AMLAlertService(db, tenant_id)
    
    def monitor_transaction(
        self,
        data: TransactionMonitoringCreate,
        user_id: Optional[UUID] = None
    ) -> AMLTransactionMonitoring:
        """
        Monitor a transaction and apply AML rules
        """
        # Create transaction monitoring record
        transaction = AMLTransactionMonitoring(
            id=uuid4(),
            tenant_id=self.tenant_id,
            transaction_id=data.transaction_id,
            transaction_type=data.transaction_type,
            transaction_date=data.transaction_date,
            posting_date=data.posting_date,
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            customer_type=data.customer_type,
            account_id=data.account_id,
            account_number=data.account_number,
            counterparty_name=data.counterparty_name,
            counterparty_account=data.counterparty_account,
            counterparty_bank=data.counterparty_bank,
            counterparty_country=data.counterparty_country,
            transaction_amount=data.transaction_amount,
            transaction_currency=data.transaction_currency,
            branch_code=data.branch_code,
            channel=data.channel,
            ip_address=data.ip_address,
            device_id=data.device_id,
            is_cash_transaction=data.is_cash_transaction,
            is_cross_border=data.is_cross_border,
            transaction_purpose=data.transaction_purpose,
            transaction_details=data.transaction_details,
            created_by=user_id,
            updated_by=user_id
        )
        
        # Get customer risk profile (simplified - would fetch from customer table)
        customer_risk_rating = self._get_customer_risk_rating(data.customer_id)
        transaction.customer_risk_rating = customer_risk_rating
        
        # Check if customer is PEP
        transaction.customer_is_pep = self._check_customer_pep_status(data.customer_id)
        
        # Apply monitoring rules
        rules_result = self._apply_monitoring_rules(transaction)
        
        transaction.rules_triggered = rules_result['rules_triggered']
        transaction.risk_score = rules_result['risk_score']
        transaction.risk_level = rules_result['risk_level']
        transaction.requires_review = rules_result['requires_review']
        
        # Save transaction
        self.db.add(transaction)
        self.db.flush()
        
        # Generate alerts if needed
        alerts_count = 0
        if rules_result['alerts']:
            for alert_data in rules_result['alerts']:
                alert_data['transaction_monitoring_id'] = transaction.id
                alert_data['customer_id'] = transaction.customer_id
                self.alert_service.create_alert(alert_data, user_id)
                alerts_count += 1
        
        transaction.alerts_generated = alerts_count
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def _apply_monitoring_rules(
        self,
        transaction: AMLTransactionMonitoring
    ) -> Dict[str, Any]:
        """
        Apply all active monitoring rules to transaction
        """
        # Get active rules
        rules = self.db.query(AMLMonitoringRule).filter(
            AMLMonitoringRule.tenant_id == self.tenant_id,
            AMLMonitoringRule.is_active == True
        ).order_by(AMLMonitoringRule.priority.desc()).all()
        
        risk_score = Decimal('0')
        rules_triggered = []
        alerts = []
        requires_review = False
        risk_level = TransactionRiskLevel.LOW
        
        for rule in rules:
            rule_result = self._evaluate_rule(rule, transaction)
            
            if rule_result['triggered']:
                rules_triggered.append(rule.rule_code)
                risk_score += rule.risk_score_addition
                
                if rule.generate_alert:
                    alerts.append({
                        'alert_type': rule.rule_code,
                        'alert_category': 'transaction',
                        'severity': rule.auto_risk_level or 'medium',
                        'alert_title': f"Rule Triggered: {rule.rule_name}",
                        'alert_description': rule_result.get('description', ''),
                        'rule_triggered': rule.rule_code,
                        'risk_score': rule.risk_score_addition,
                        'risk_indicators': rule_result.get('indicators', [])
                    })
                
                if rule.require_review:
                    requires_review = True
                
                if rule.auto_risk_level:
                    current_level = self._get_risk_level_value(risk_level)
                    new_level = self._get_risk_level_value(rule.auto_risk_level)
                    if new_level > current_level:
                        risk_level = TransactionRiskLevel(rule.auto_risk_level)
        
        # Determine overall risk level based on score if not set by rule
        if not rules_triggered:
            risk_level = self._calculate_risk_level(risk_score)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'rules_triggered': rules_triggered,
            'alerts': alerts,
            'requires_review': requires_review
        }
    
    def _evaluate_rule(
        self,
        rule: AMLMonitoringRule,
        transaction: AMLTransactionMonitoring
    ) -> Dict[str, Any]:
        """
        Evaluate a specific rule against transaction
        """
        result = {'triggered': False, 'indicators': [], 'description': ''}
        
        if rule.rule_type == 'threshold':
            # Single transaction threshold
            if rule.threshold_amount and transaction.transaction_amount >= rule.threshold_amount:
                result['triggered'] = True
                result['description'] = f"Transaction amount {transaction.transaction_amount} exceeds threshold {rule.threshold_amount}"
                result['indicators'].append({
                    'type': 'amount_threshold',
                    'value': float(transaction.transaction_amount),
                    'threshold': float(rule.threshold_amount)
                })
        
        elif rule.rule_type == 'velocity':
            # Velocity check - multiple transactions in time period
            if rule.time_period_days and rule.threshold_count:
                start_date = transaction.transaction_date - timedelta(days=rule.time_period_days)
                
                count = self.db.query(func.count(AMLTransactionMonitoring.id)).filter(
                    AMLTransactionMonitoring.tenant_id == self.tenant_id,
                    AMLTransactionMonitoring.customer_id == transaction.customer_id,
                    AMLTransactionMonitoring.transaction_date >= start_date,
                    AMLTransactionMonitoring.transaction_date <= transaction.transaction_date
                ).scalar()
                
                if count >= rule.threshold_count:
                    result['triggered'] = True
                    result['description'] = f"{count} transactions in {rule.time_period_days} days exceeds threshold {rule.threshold_count}"
                    result['indicators'].append({
                        'type': 'velocity',
                        'count': count,
                        'period_days': rule.time_period_days,
                        'threshold': rule.threshold_count
                    })
        
        elif rule.rule_type == 'pattern':
            # Pattern-based rules (structured transactions, round amounts, etc.)
            if rule.rule_config:
                config = rule.rule_config
                
                # Check for structured transactions (multiple transactions just below threshold)
                if config.get('check_structuring'):
                    structuring_threshold = config.get('structuring_threshold', 1000000)  # 10 lakh
                    if transaction.transaction_amount >= structuring_threshold * 0.8:
                        # Check recent transactions
                        recent_count = self._check_recent_similar_transactions(
                            transaction, 
                            days=1,
                            amount_variance=0.1
                        )
                        if recent_count >= 2:
                            result['triggered'] = True
                            result['description'] = f"Potential structuring detected: {recent_count} similar transactions"
                            result['indicators'].append({
                                'type': 'structuring',
                                'similar_transactions': recent_count
                            })
                
                # Check for round amounts
                if config.get('check_round_amounts'):
                    if self._is_round_amount(transaction.transaction_amount):
                        result['triggered'] = True
                        result['description'] = "Round amount transaction"
                        result['indicators'].append({'type': 'round_amount'})
        
        elif rule.rule_type == 'geographic':
            # Geographic risk checks
            if transaction.is_cross_border:
                high_risk_countries = rule.rule_config.get('high_risk_countries', []) if rule.rule_config else []
                if transaction.counterparty_country in high_risk_countries:
                    result['triggered'] = True
                    result['description'] = f"Transaction to/from high-risk country: {transaction.counterparty_country}"
                    result['indicators'].append({
                        'type': 'high_risk_country',
                        'country': transaction.counterparty_country
                    })
                    transaction.is_high_risk_country = True
        
        elif rule.rule_type == 'customer_behavior':
            # Customer behavior anomaly detection
            avg_amount = self._get_customer_avg_transaction_amount(transaction.customer_id)
            if avg_amount and transaction.transaction_amount > avg_amount * 5:
                result['triggered'] = True
                result['description'] = f"Transaction amount significantly higher than customer average"
                result['indicators'].append({
                    'type': 'deviation_from_average',
                    'amount': float(transaction.transaction_amount),
                    'average': float(avg_amount),
                    'deviation_factor': float(transaction.transaction_amount / avg_amount)
                })
        
        return result
    
    def _check_recent_similar_transactions(
        self,
        transaction: AMLTransactionMonitoring,
        days: int,
        amount_variance: float
    ) -> int:
        """Check for similar recent transactions"""
        start_date = transaction.transaction_date - timedelta(days=days)
        min_amount = transaction.transaction_amount * (1 - amount_variance)
        max_amount = transaction.transaction_amount * (1 + amount_variance)
        
        count = self.db.query(func.count(AMLTransactionMonitoring.id)).filter(
            AMLTransactionMonitoring.tenant_id == self.tenant_id,
            AMLTransactionMonitoring.customer_id == transaction.customer_id,
            AMLTransactionMonitoring.transaction_date >= start_date,
            AMLTransactionMonitoring.transaction_date < transaction.transaction_date,
            AMLTransactionMonitoring.transaction_amount >= min_amount,
            AMLTransactionMonitoring.transaction_amount <= max_amount
        ).scalar()
        
        return count
    
    def _is_round_amount(self, amount: Decimal) -> bool:
        """Check if amount is a round number"""
        return amount % 100000 == 0 or amount % 50000 == 0
    
    def _get_customer_avg_transaction_amount(self, customer_id: UUID) -> Optional[Decimal]:
        """Get customer's average transaction amount"""
        result = self.db.query(
            func.avg(AMLTransactionMonitoring.transaction_amount)
        ).filter(
            AMLTransactionMonitoring.tenant_id == self.tenant_id,
            AMLTransactionMonitoring.customer_id == customer_id
        ).scalar()
        
        return result
    
    def _get_customer_risk_rating(self, customer_id: UUID) -> str:
        """Get customer risk rating (simplified)"""
        # In real implementation, would fetch from customer table
        return "medium"
    
    def _check_customer_pep_status(self, customer_id: UUID) -> bool:
        """Check if customer is a PEP (simplified)"""
        from backend.shared.database.aml_models import AMLPEPScreening, ScreeningStatus
        
        pep_screening = self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id,
            AMLPEPScreening.customer_id == customer_id,
            AMLPEPScreening.is_pep == True,
            AMLPEPScreening.screening_status == ScreeningStatus.CONFIRMED_MATCH
        ).first()
        
        return pep_screening is not None
    
    def _get_risk_level_value(self, risk_level: str) -> int:
        """Convert risk level to numeric value for comparison"""
        mapping = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return mapping.get(risk_level, 1)
    
    def _calculate_risk_level(self, risk_score: Decimal) -> TransactionRiskLevel:
        """Calculate risk level based on risk score"""
        if risk_score >= 80:
            return TransactionRiskLevel.CRITICAL
        elif risk_score >= 50:
            return TransactionRiskLevel.HIGH
        elif risk_score >= 25:
            return TransactionRiskLevel.MEDIUM
        else:
            return TransactionRiskLevel.LOW
    
    def get_transaction_monitoring(
        self,
        transaction_id: UUID
    ) -> Optional[AMLTransactionMonitoring]:
        """Get transaction monitoring record"""
        return self.db.query(AMLTransactionMonitoring).filter(
            AMLTransactionMonitoring.tenant_id == self.tenant_id,
            AMLTransactionMonitoring.id == transaction_id
        ).first()
    
    def list_transactions(
        self,
        filters: TransactionMonitoringFilter,
        skip: int = 0,
        limit: int = 100
    ) -> List[AMLTransactionMonitoring]:
        """List transaction monitoring records with filters"""
        query = self.db.query(AMLTransactionMonitoring).filter(
            AMLTransactionMonitoring.tenant_id == self.tenant_id
        )
        
        if filters.start_date:
            query = query.filter(AMLTransactionMonitoring.posting_date >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(AMLTransactionMonitoring.posting_date <= filters.end_date)
        
        if filters.customer_id:
            query = query.filter(AMLTransactionMonitoring.customer_id == filters.customer_id)
        
        if filters.risk_level:
            query = query.filter(AMLTransactionMonitoring.risk_level == filters.risk_level)
        
        if filters.min_amount:
            query = query.filter(AMLTransactionMonitoring.transaction_amount >= filters.min_amount)
        
        if filters.max_amount:
            query = query.filter(AMLTransactionMonitoring.transaction_amount <= filters.max_amount)
        
        if filters.transaction_type:
            query = query.filter(AMLTransactionMonitoring.transaction_type == filters.transaction_type)
        
        if filters.requires_review is not None:
            query = query.filter(AMLTransactionMonitoring.requires_review == filters.requires_review)
        
        if filters.is_cash_transaction is not None:
            query = query.filter(AMLTransactionMonitoring.is_cash_transaction == filters.is_cash_transaction)
        
        query = query.order_by(desc(AMLTransactionMonitoring.transaction_date))
        
        return query.offset(skip).limit(limit).all()
    
    def update_review_status(
        self,
        transaction_id: UUID,
        status: str,
        notes: str,
        user_id: UUID
    ) -> Optional[AMLTransactionMonitoring]:
        """Update transaction review status"""
        transaction = self.get_transaction_monitoring(transaction_id)
        
        if not transaction:
            return None
        
        transaction.review_status = status
        transaction.reviewed_by = user_id
        transaction.reviewed_at = datetime.utcnow()
        transaction.review_notes = notes
        transaction.updated_by = user_id
        transaction.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(transaction)
        
        return transaction
    
    def get_transaction_statistics(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get transaction monitoring statistics"""
        query = self.db.query(AMLTransactionMonitoring).filter(
            AMLTransactionMonitoring.tenant_id == self.tenant_id
        )
        
        if start_date:
            query = query.filter(AMLTransactionMonitoring.posting_date >= start_date)
        
        if end_date:
            query = query.filter(AMLTransactionMonitoring.posting_date <= end_date)
        
        total = query.count()
        
        high_risk = query.filter(
            AMLTransactionMonitoring.risk_level == TransactionRiskLevel.HIGH
        ).count()
        
        critical = query.filter(
            AMLTransactionMonitoring.risk_level == TransactionRiskLevel.CRITICAL
        ).count()
        
        cash_transactions = query.filter(
            AMLTransactionMonitoring.is_cash_transaction == True
        ).count()
        
        cross_border = query.filter(
            AMLTransactionMonitoring.is_cross_border == True
        ).count()
        
        requires_review = query.filter(
            AMLTransactionMonitoring.requires_review == True
        ).count()
        
        total_amount = self.db.query(
            func.sum(AMLTransactionMonitoring.transaction_amount)
        ).filter(
            AMLTransactionMonitoring.tenant_id == self.tenant_id
        ).scalar() or Decimal('0')
        
        return {
            'total_transactions': total,
            'high_risk_count': high_risk,
            'critical_risk_count': critical,
            'cash_transactions': cash_transactions,
            'cross_border_transactions': cross_border,
            'requires_review': requires_review,
            'total_amount': total_amount
        }
