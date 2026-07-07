"""
Compliance Alert Service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

from shared.database.compliance_models import ComplianceAlert
from .schemas import ComplianceAlertCreate, ComplianceAlertResponse


class ComplianceAlertService:
    """Service for compliance alerts"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_alert(
        self,
        data: ComplianceAlertCreate,
        user_id: UUID
    ) -> ComplianceAlert:
        """Create compliance alert"""
        import uuid
        
        alert = ComplianceAlert(
            id=uuid.uuid4(),
            tenant_id=self.tenant_id,
            alert_type=data.alert_type,
            alert_category=data.alert_category,
            severity=data.severity,
            borrower_id=data.borrower_id,
            loan_account_id=data.loan_account_id,
            alert_message=data.alert_message,
            alert_details=data.alert_details,
            status='open',
            due_date=data.due_date,
            is_overdue=False,
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_alert(self, alert_id: UUID) -> Optional[ComplianceAlert]:
        """Get alert by ID"""
        return self.db.query(ComplianceAlert).filter(
            ComplianceAlert.id == alert_id,
            ComplianceAlert.tenant_id == self.tenant_id,
            ComplianceAlert.is_deleted == False
        ).first()
    
    def list_alerts(
        self,
        status: Optional[str] = None,
        alert_type: Optional[str] = None,
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ComplianceAlert]:
        """List alerts with filters"""
        
        query = self.db.query(ComplianceAlert).filter(
            ComplianceAlert.tenant_id == self.tenant_id,
            ComplianceAlert.is_deleted == False
        )
        
        if status:
            query = query.filter(ComplianceAlert.status == status)
        
        if alert_type:
            query = query.filter(ComplianceAlert.alert_type == alert_type)
        
        if severity:
            query = query.filter(ComplianceAlert.severity == severity)
        
        query = query.order_by(
            ComplianceAlert.severity.desc(),
            ComplianceAlert.created_at.desc()
        )
        
        return query.offset(skip).limit(limit).all()
    
    def acknowledge_alert(
        self,
        alert_id: UUID,
        user_id: UUID
    ) -> Optional[ComplianceAlert]:
        """Acknowledge alert"""
        
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        
        alert.status = 'acknowledged'
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.utcnow()
        alert.updated_by = user_id
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def resolve_alert(
        self,
        alert_id: UUID,
        resolution_notes: str,
        user_id: UUID
    ) -> Optional[ComplianceAlert]:
        """Resolve alert"""
        
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        
        alert.status = 'resolved'
        alert.resolved_by = user_id
        alert.resolved_at = datetime.utcnow()
        alert.resolution_notes = resolution_notes
        alert.updated_by = user_id
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def dismiss_alert(
        self,
        alert_id: UUID,
        user_id: UUID
    ) -> Optional[ComplianceAlert]:
        """Dismiss alert"""
        
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        
        alert.status = 'dismissed'
        alert.updated_by = user_id
        alert.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def update_overdue_status(self) -> int:
        """Update overdue status for alerts past due date"""
        
        today = date.today()
        
        alerts = self.db.query(ComplianceAlert).filter(
            ComplianceAlert.tenant_id == self.tenant_id,
            ComplianceAlert.status == 'open',
            ComplianceAlert.due_date < today,
            ComplianceAlert.is_overdue == False,
            ComplianceAlert.is_deleted == False
        ).all()
        
        count = 0
        for alert in alerts:
            alert.is_overdue = True
            count += 1
        
        self.db.commit()
        
        return count
