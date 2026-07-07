"""
PEP (Politically Exposed Person) Screening Service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from backend.shared.database.aml_models import (
    AMLPEPScreening,
    ScreeningStatus,
    PEPCategory,
    AMLAuditLog
)
from backend.services.aml.schemas import (
    PEPScreeningCreate,
    PEPScreeningUpdate,
    PEPEDDCompletion
)


class PEPScreeningService:
    """Service for PEP screening and management"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    def create_screening(
        self,
        data: PEPScreeningCreate,
        user_id: Optional[UUID] = None
    ) -> AMLPEPScreening:
        """Create a new PEP screening"""
        screening_id = self._generate_screening_id()
        
        screening = AMLPEPScreening(
            id=uuid4(),
            tenant_id=self.tenant_id,
            screening_id=screening_id,
            screening_date=datetime.utcnow(),
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            date_of_birth=data.date_of_birth,
            nationality=data.nationality,
            screening_type=data.screening_type,
            trigger_event=data.trigger_event,
            screening_status=ScreeningStatus.PENDING_REVIEW,
            is_pep=False,
            edd_required=False,
            edd_completed=False,
            review_frequency_months=12,
            screening_source='manual',
            created_by=user_id,
            updated_by=user_id
        )
        
        # Perform automated screening
        screening_result = self._perform_automated_screening(screening)
        
        if screening_result['potential_match']:
            screening.is_pep = screening_result['is_pep']
            screening.pep_category = screening_result.get('pep_category')
            screening.match_score = screening_result.get('match_score')
            screening.match_details = screening_result.get('match_details')
            screening.screening_status = ScreeningStatus.POTENTIAL_MATCH
        else:
            screening.screening_status = ScreeningStatus.CLEAR
        
        # Calculate next review date
        screening.next_review_date = self._calculate_next_review_date(
            screening.screening_type,
            screening.is_pep
        )
        
        self.db.add(screening)
        
        # Log screening
        self._log_audit(
            event_type='pep_screening_created',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Created PEP screening {screening_id}",
            action_details={
                'customer_name': data.customer_name,
                'screening_type': data.screening_type,
                'result': screening.screening_status.value
            }
        )
        
        self.db.commit()
        self.db.refresh(screening)
        
        return screening
    
    def _perform_automated_screening(
        self,
        screening: AMLPEPScreening
    ) -> Dict[str, Any]:
        """
        Perform automated PEP screening
        In production, this would integrate with external PEP databases
        """
        result = {
            'potential_match': False,
            'is_pep': False,
            'match_score': None,
            'match_details': None,
            'pep_category': None
        }
        
        # Simplified screening logic
        # In production, integrate with:
        # - World-Check
        # - Dow Jones
        # - LexisNexis
        # - Internal PEP database
        
        # Example: Check customer name against known patterns
        name_lower = screening.customer_name.lower()
        
        # High-profile keywords (simplified example)
        pep_keywords = [
            'minister', 'governor', 'ambassador', 'senator',
            'member of parliament', 'mp', 'chairman', 'ceo public'
        ]
        
        for keyword in pep_keywords:
            if keyword in name_lower:
                result['potential_match'] = True
                result['is_pep'] = True
                result['match_score'] = Decimal('75.0')
                result['pep_category'] = PEPCategory.DOMESTIC_PEP
                result['match_details'] = {
                    'matched_keyword': keyword,
                    'match_type': 'keyword',
                    'requires_manual_review': True
                }
                break
        
        return result
    
    def get_screening(self, screening_id: UUID) -> Optional[AMLPEPScreening]:
        """Get PEP screening by ID"""
        return self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id,
            AMLPEPScreening.id == screening_id
        ).first()
    
    def list_screenings(
        self,
        customer_id: Optional[UUID] = None,
        screening_status: Optional[str] = None,
        is_pep: Optional[bool] = None,
        screening_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AMLPEPScreening]:
        """List PEP screenings with filters"""
        query = self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id
        )
        
        if customer_id:
            query = query.filter(AMLPEPScreening.customer_id == customer_id)
        
        if screening_status:
            query = query.filter(AMLPEPScreening.screening_status == screening_status)
        
        if is_pep is not None:
            query = query.filter(AMLPEPScreening.is_pep == is_pep)
        
        if screening_type:
            query = query.filter(AMLPEPScreening.screening_type == screening_type)
        
        query = query.order_by(desc(AMLPEPScreening.screening_date))
        
        return query.offset(skip).limit(limit).all()
    
    def update_screening(
        self,
        screening_id: UUID,
        data: PEPScreeningUpdate,
        user_id: UUID
    ) -> Optional[AMLPEPScreening]:
        """Update PEP screening result"""
        screening = self.get_screening(screening_id)
        
        if not screening:
            return None
        
        old_values = {
            'screening_status': screening.screening_status.value,
            'is_pep': screening.is_pep
        }
        
        screening.screening_status = ScreeningStatus(data.screening_status)
        screening.is_pep = data.is_pep
        
        if data.pep_category:
            screening.pep_category = PEPCategory(data.pep_category)
        
        if data.match_score is not None:
            screening.match_score = data.match_score
        
        if data.match_details:
            screening.match_details = data.match_details
        
        if data.pep_position:
            screening.pep_position = data.pep_position
        
        if data.pep_organization:
            screening.pep_organization = data.pep_organization
        
        if data.pep_country:
            screening.pep_country = data.pep_country
        
        if data.pep_start_date:
            screening.pep_start_date = data.pep_start_date
        
        if data.pep_end_date:
            screening.pep_end_date = data.pep_end_date
        
        screening.edd_required = data.edd_required
        
        if data.source_of_wealth:
            screening.source_of_wealth = data.source_of_wealth
        
        if data.source_of_funds:
            screening.source_of_funds = data.source_of_funds
        
        if data.risk_rating:
            screening.risk_rating = data.risk_rating
        
        screening.updated_by = user_id
        screening.updated_at = datetime.utcnow()
        
        new_values = {
            'screening_status': screening.screening_status.value,
            'is_pep': screening.is_pep
        }
        
        # Log update
        self._log_audit(
            event_type='pep_screening_updated',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Updated PEP screening {screening.screening_id}",
            action_details={
                'old_values': old_values,
                'new_values': new_values
            }
        )
        
        self.db.commit()
        self.db.refresh(screening)
        
        return screening
    
    def complete_edd(
        self,
        screening_id: UUID,
        edd: PEPEDDCompletion,
        user_id: UUID
    ) -> Optional[AMLPEPScreening]:
        """Complete Enhanced Due Diligence for PEP"""
        screening = self.get_screening(screening_id)
        
        if not screening:
            return None
        
        if not screening.is_pep:
            raise ValueError("EDD can only be completed for confirmed PEPs")
        
        screening.edd_completed = True
        screening.edd_completion_date = date.today()
        screening.edd_summary = edd.edd_summary
        screening.source_of_wealth = edd.source_of_wealth
        screening.source_of_funds = edd.source_of_funds
        screening.risk_rating = edd.risk_rating
        screening.approved_by = user_id
        screening.approved_at = datetime.utcnow()
        screening.approval_remarks = edd.approval_remarks
        screening.screening_status = ScreeningStatus.CONFIRMED_MATCH
        screening.updated_by = user_id
        screening.updated_at = datetime.utcnow()
        
        # Set next review date based on risk rating
        if edd.risk_rating in ['high', 'very_high']:
            screening.review_frequency_months = 6
        else:
            screening.review_frequency_months = 12
        
        screening.next_review_date = date.today() + timedelta(
            days=screening.review_frequency_months * 30
        )
        
        # Log EDD completion
        self._log_audit(
            event_type='pep_edd_completed',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Completed EDD for {screening.screening_id}",
            action_details={
                'risk_rating': edd.risk_rating,
                'next_review': screening.next_review_date.isoformat()
            }
        )
        
        self.db.commit()
        self.db.refresh(screening)
        
        return screening
    
    def mark_false_positive(
        self,
        screening_id: UUID,
        reason: str,
        user_id: UUID
    ) -> Optional[AMLPEPScreening]:
        """Mark screening as false positive"""
        screening = self.get_screening(screening_id)
        
        if not screening:
            return None
        
        screening.screening_status = ScreeningStatus.FALSE_POSITIVE
        screening.is_pep = False
        screening.approval_remarks = f"False Positive: {reason}"
        screening.approved_by = user_id
        screening.approved_at = datetime.utcnow()
        screening.updated_by = user_id
        screening.updated_at = datetime.utcnow()
        
        # Log false positive
        self._log_audit(
            event_type='pep_false_positive',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Marked {screening.screening_id} as false positive",
            action_details={'reason': reason}
        )
        
        self.db.commit()
        self.db.refresh(screening)
        
        return screening
    
    def get_due_for_review(self) -> List[AMLPEPScreening]:
        """Get PEP screenings due for review"""
        today = date.today()
        
        return self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id,
            AMLPEPScreening.is_pep == True,
            AMLPEPScreening.next_review_date <= today,
            AMLPEPScreening.screening_status == ScreeningStatus.CONFIRMED_MATCH
        ).all()
    
    def get_pep_statistics(self) -> Dict[str, Any]:
        """Get PEP screening statistics"""
        total = self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id
        ).count()
        
        confirmed_peps = self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id,
            AMLPEPScreening.is_pep == True,
            AMLPEPScreening.screening_status == ScreeningStatus.CONFIRMED_MATCH
        ).count()
        
        pending_review = self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id,
            AMLPEPScreening.screening_status.in_([
                ScreeningStatus.PENDING_REVIEW,
                ScreeningStatus.POTENTIAL_MATCH
            ])
        ).count()
        
        edd_required = self.db.query(AMLPEPScreening).filter(
            AMLPEPScreening.tenant_id == self.tenant_id,
            AMLPEPScreening.edd_required == True,
            AMLPEPScreening.edd_completed == False
        ).count()
        
        due_for_review = len(self.get_due_for_review())
        
        # By PEP category
        by_category = dict(
            self.db.query(
                AMLPEPScreening.pep_category,
                func.count(AMLPEPScreening.id)
            ).filter(
                AMLPEPScreening.tenant_id == self.tenant_id,
                AMLPEPScreening.is_pep == True
            ).group_by(AMLPEPScreening.pep_category).all()
        )
        
        return {
            'total_screenings': total,
            'confirmed_peps': confirmed_peps,
            'pending_review': pending_review,
            'edd_required': edd_required,
            'due_for_review': due_for_review,
            'by_category': {k.value if k else 'unknown': v for k, v in by_category.items()}
        }
    
    def _calculate_next_review_date(
        self,
        screening_type: str,
        is_pep: bool
    ) -> date:
        """Calculate next review date"""
        if not is_pep:
            # Regular customers - annual review
            months = 12
        else:
            # PEPs - more frequent reviews
            months = 6
        
        return date.today() + timedelta(days=months * 30)
    
    def _generate_screening_id(self) -> str:
        """Generate unique screening ID"""
        prefix = "PEP"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        count = self.db.query(func.count(AMLPEPScreening.id)).filter(
            AMLPEPScreening.tenant_id == self.tenant_id,
            func.date(AMLPEPScreening.created_at) == date.today()
        ).scalar() or 0
        
        return f"{prefix}{date_str}{count + 1:05d}"
    
    def _log_audit(
        self,
        event_type: str,
        user_id: Optional[UUID],
        reference_id: str,
        action: str,
        action_details: Optional[Dict] = None
    ):
        """Log audit entry"""
        log = AMLAuditLog(
            id=uuid4(),
            tenant_id=self.tenant_id,
            event_type=event_type,
            event_category='screening',
            event_date=datetime.utcnow(),
            user_id=user_id,
            reference_type='pep_screening',
            reference_id=reference_id,
            action=action,
            action_details=action_details,
            result='success'
        )
        
        self.db.add(log)
