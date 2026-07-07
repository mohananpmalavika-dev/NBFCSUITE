"""
AML Alert Management Service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from backend.shared.database.aml_models import (
    AMLAlert,
    AlertStatus,
    AMLAlertWorkflow,
    AMLAuditLog
)
from backend.services.aml.schemas import (
    AMLAlertCreate,
    AMLAlertAssignment,
    AMLAlertReview,
    AMLAlertClose
)


class AMLAlertService:
    """Service for AML alert management"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_alert(
        self,
        data: Dict[str, Any],
        user_id: Optional[UUID] = None
    ) -> AMLAlert:
        """Create a new AML alert"""
        alert_id = self._generate_alert_id()
        
        # Calculate due date based on severity
        severity = data.get('severity', 'medium')
        due_date = self._calculate_due_date(severity)
        
        alert = AMLAlert(
            id=uuid4(),
            tenant_id=self.tenant_id,
            alert_id=alert_id,
            alert_type=data['alert_type'],
            alert_category=data['alert_category'],
            severity=data['severity'],
            transaction_monitoring_id=data.get('transaction_monitoring_id'),
            customer_id=data.get('customer_id'),
            alert_title=data['alert_title'],
            alert_description=data.get('alert_description'),
            rule_triggered=data.get('rule_triggered'),
            risk_score=data.get('risk_score', Decimal('0')),
            risk_indicators=data.get('risk_indicators', []),
            status=AlertStatus.OPEN,
            due_date=due_date,
            is_overdue=False,
            escalation_level=0,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(alert)
        self.db.flush()
        
        # Log alert creation
        self._log_audit(
            event_type='alert_created',
            event_category='alert',
            user_id=user_id,
            reference_type='alert',
            reference_id=str(alert.id),
            action=f"Created alert {alert_id}",
            action_details={
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'customer_id': str(alert.customer_id) if alert.customer_id else None
            }
        )
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_alert(self, alert_id: UUID) -> Optional[AMLAlert]:
        """Get alert by ID"""
        return self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id,
            AMLAlert.id == alert_id
        ).first()
    
    def list_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        assigned_to: Optional[UUID] = None,
        customer_id: Optional[UUID] = None,
        alert_type: Optional[str] = None,
        is_overdue: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AMLAlert]:
        """List alerts with filters"""
        query = self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id
        )
        
        if status:
            query = query.filter(AMLAlert.status == status)
        
        if severity:
            query = query.filter(AMLAlert.severity == severity)
        
        if assigned_to:
            query = query.filter(AMLAlert.assigned_to == assigned_to)
        
        if customer_id:
            query = query.filter(AMLAlert.customer_id == customer_id)
        
        if alert_type:
            query = query.filter(AMLAlert.alert_type == alert_type)
        
        if is_overdue is not None:
            query = query.filter(AMLAlert.is_overdue == is_overdue)
        
        query = query.order_by(desc(AMLAlert.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    def assign_alert(
        self,
        alert_id: UUID,
        assigned_to: UUID,
        user_id: UUID
    ) -> Optional[AMLAlert]:
        """Assign alert to user"""
        alert = self.get_alert(alert_id)
        
        if not alert:
            return None
        
        old_assignee = alert.assigned_to
        
        alert.assigned_to = assigned_to
        alert.assigned_at = datetime.utcnow()
        alert.updated_by = user_id
        alert.updated_at = datetime.utcnow()
        
        # Create workflow entry
        workflow = AMLAlertWorkflow(
            id=uuid4(),
            tenant_id=self.tenant_id,
            alert_id=alert.id,
            workflow_step='assignment',
            step_sequence=1,
            assigned_to=assigned_to,
            assigned_at=datetime.utcnow(),
            assigned_by=user_id,
            status='pending',
            sla_due_date=alert.due_date,
            created_by=user_id
        )
        
        self.db.add(workflow)
        
        # Log assignment
        self._log_audit(
            event_type='alert_assigned',
            event_category='alert',
            user_id=user_id,
            reference_type='alert',
            reference_id=str(alert.id),
            action=f"Assigned alert to user",
            action_details={
                'old_assignee': str(old_assignee) if old_assignee else None,
                'new_assignee': str(assigned_to)
            }
        )
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def review_alert(
        self,
        alert_id: UUID,
        review: AMLAlertReview,
        user_id: UUID
    ) -> Optional[AMLAlert]:
        """Review and update alert"""
        alert = self.get_alert(alert_id)
        
        if not alert:
            return None
        
        alert.status = AlertStatus.UNDER_REVIEW
        alert.investigation_notes = review.investigation_notes
        alert.false_positive = review.false_positive
        alert.reviewed_by = user_id
        alert.reviewed_at = datetime.utcnow()
        alert.updated_by = user_id
        alert.updated_at = datetime.utcnow()
        
        # Log review
        self._log_audit(
            event_type='alert_reviewed',
            event_category='alert',
            user_id=user_id,
            reference_type='alert',
            reference_id=str(alert.id),
            action=f"Reviewed alert",
            action_details={
                'false_positive': review.false_positive,
                'has_notes': len(review.investigation_notes) > 0
            }
        )
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def close_alert(
        self,
        alert_id: UUID,
        closure: AMLAlertClose,
        user_id: UUID
    ) -> Optional[AMLAlert]:
        """Close an alert"""
        alert = self.get_alert(alert_id)
        
        if not alert:
            return None
        
        # Set status based on resolution
        if closure.resolution == 'false_positive':
            alert.status = AlertStatus.CLOSED_FALSE_POSITIVE
            alert.false_positive = True
        elif closure.resolution == 'reported':
            alert.status = AlertStatus.CLOSED_REPORTED
        else:
            alert.status = AlertStatus.CLOSED_NO_ACTION
        
        alert.investigation_notes = (alert.investigation_notes or "") + f"\n\nClosure: {closure.notes}"
        alert.closed_by = user_id
        alert.closed_at = datetime.utcnow()
        alert.updated_by = user_id
        alert.updated_at = datetime.utcnow()
        
        # Log closure
        self._log_audit(
            event_type='alert_closed',
            event_category='alert',
            user_id=user_id,
            reference_type='alert',
            reference_id=str(alert.id),
            action=f"Closed alert - {closure.resolution}",
            action_details={
                'resolution': closure.resolution,
                'status': alert.status.value
            }
        )
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def escalate_alert(
        self,
        alert_id: UUID,
        reason: str,
        user_id: UUID
    ) -> Optional[AMLAlert]:
        """Escalate an alert"""
        alert = self.get_alert(alert_id)
        
        if not alert:
            return None
        
        alert.status = AlertStatus.ESCALATED
        alert.escalation_level += 1
        alert.investigation_notes = (alert.investigation_notes or "") + f"\n\nEscalated (Level {alert.escalation_level}): {reason}"
        alert.updated_by = user_id
        alert.updated_at = datetime.utcnow()
        
        # Log escalation
        self._log_audit(
            event_type='alert_escalated',
            event_category='alert',
            user_id=user_id,
            reference_type='alert',
            reference_id=str(alert.id),
            action=f"Escalated alert to level {alert.escalation_level}",
            action_details={
                'escalation_level': alert.escalation_level,
                'reason': reason
            }
        )
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def check_overdue_alerts(self):
        """Check and mark overdue alerts"""
        now = datetime.utcnow()
        
        overdue_alerts = self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id,
            AMLAlert.status.in_([AlertStatus.OPEN, AlertStatus.UNDER_REVIEW]),
            AMLAlert.due_date < now,
            AMLAlert.is_overdue == False
        ).all()
        
        for alert in overdue_alerts:
            alert.is_overdue = True
            alert.updated_at = datetime.utcnow()
        
        if overdue_alerts:
            self.db.commit()
        
        return len(overdue_alerts)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total = self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id
        ).count()
        
        open_alerts = self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id,
            AMLAlert.status == AlertStatus.OPEN
        ).count()
        
        under_review = self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id,
            AMLAlert.status == AlertStatus.UNDER_REVIEW
        ).count()
        
        escalated = self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id,
            AMLAlert.status == AlertStatus.ESCALATED
        ).count()
        
        overdue = self.db.query(AMLAlert).filter(
            AMLAlert.tenant_id == self.tenant_id,
            AMLAlert.is_overdue == True,
            AMLAlert.status.in_([AlertStatus.OPEN, AlertStatus.UNDER_REVIEW, AlertStatus.ESCALATED])
        ).count()
        
        # Alerts by type
        alerts_by_type = dict(
            self.db.query(
                AMLAlert.alert_type,
                func.count(AMLAlert.id)
            ).filter(
                AMLAlert.tenant_id == self.tenant_id
            ).group_by(AMLAlert.alert_type).all()
        )
        
        # Alerts by severity
        alerts_by_severity = dict(
            self.db.query(
                AMLAlert.severity,
                func.count(AMLAlert.id)
            ).filter(
                AMLAlert.tenant_id == self.tenant_id
            ).group_by(AMLAlert.severity).all()
        )
        
        return {
            'total_alerts': total,
            'open_alerts': open_alerts,
            'under_review': under_review,
            'escalated': escalated,
            'overdue_alerts': overdue,
            'alerts_by_type': alerts_by_type,
            'alerts_by_severity': alerts_by_severity
        }
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        prefix = "AML"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        # Get count for today
        count = self.db.query(func.count(AMLAlert.id)).filter(
            AMLAlert.tenant_id == self.tenant_id,
            func.date(AMLAlert.created_at) == date.today()
        ).scalar() or 0
        
        return f"{prefix}{date_str}{count + 1:05d}"
    
    def _calculate_due_date(self, severity: str) -> datetime:
        """Calculate due date based on severity"""
        now = datetime.utcnow()
        
        # SLA in hours
        sla_mapping = {
            'low': 72,      # 3 days
            'medium': 48,   # 2 days
            'high': 24,     # 1 day
            'critical': 4   # 4 hours
        }
        
        hours = sla_mapping.get(severity, 48)
        return now + timedelta(hours=hours)
    
    def _log_audit(
        self,
        event_type: str,
        event_category: str,
        user_id: Optional[UUID],
        reference_type: str,
        reference_id: str,
        action: str,
        action_details: Optional[Dict] = None,
        result: str = 'success'
    ):
        """Log audit entry"""
        log = AMLAuditLog(
            id=uuid4(),
            tenant_id=self.tenant_id,
            event_type=event_type,
            event_category=event_category,
            event_date=datetime.utcnow(),
            user_id=user_id,
            reference_type=reference_type,
            reference_id=reference_id,
            action=action,
            action_details=action_details,
            result=result
        )
        
        self.db.add(log)
