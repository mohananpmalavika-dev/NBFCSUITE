"""
Sanction List Screening Service
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from difflib import SequenceMatcher

from backend.shared.database.aml_models import (
    AMLSanctionList,
    AMLSanctionScreening,
    ScreeningStatus,
    TransactionRiskLevel,
    AMLAuditLog
)
from backend.services.aml.schemas import (
    SanctionListCreate,
    SanctionScreeningCreate,
    SanctionScreeningUpdate
)


class SanctionScreeningService:
    """Service for sanction list screening and management"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    # ========================================================================
    # SANCTION LIST MANAGEMENT
    # ========================================================================
    
    def create_sanction_list_entry(
        self,
        data: SanctionListCreate,
        user_id: Optional[UUID] = None
    ) -> AMLSanctionList:
        """Add entry to sanction list"""
        sanction = AMLSanctionList(
            id=uuid4(),
            tenant_id=self.tenant_id,
            list_id=data.list_id,
            list_name=data.list_name,
            list_type=data.list_type,
            list_source=data.list_source,
            list_url=data.list_url,
            entity_name=data.entity_name,
            entity_type=data.entity_type,
            aliases=data.aliases,
            date_of_birth=data.date_of_birth,
            place_of_birth=data.place_of_birth,
            nationality=data.nationality,
            passport_numbers=data.passport_numbers,
            identification_numbers=data.identification_numbers,
            addresses=data.addresses,
            sanction_type=data.sanction_type,
            sanction_reason=data.sanction_reason,
            designation_date=data.designation_date,
            is_active=data.is_active,
            additional_info=data.additional_info,
            last_updated=datetime.utcnow(),
            created_by=user_id,
            updated_by=user_id
        )
        
        self.db.add(sanction)
        
        # Log creation
        self._log_audit(
            event_type='sanction_list_entry_created',
            user_id=user_id,
            reference_id=str(sanction.id),
            action=f"Added sanction list entry: {data.entity_name}",
            action_details={
                'list_type': data.list_type,
                'entity_name': data.entity_name
            }
        )
        
        self.db.commit()
        self.db.refresh(sanction)
        
        return sanction
    
    def get_sanction_list_entry(
        self,
        sanction_id: UUID
    ) -> Optional[AMLSanctionList]:
        """Get sanction list entry"""
        return self.db.query(AMLSanctionList).filter(
            AMLSanctionList.tenant_id == self.tenant_id,
            AMLSanctionList.id == sanction_id
        ).first()
    
    def list_sanction_entries(
        self,
        list_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_name: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AMLSanctionList]:
        """List sanction list entries"""
        query = self.db.query(AMLSanctionList).filter(
            AMLSanctionList.tenant_id == self.tenant_id
        )
        
        if list_type:
            query = query.filter(AMLSanctionList.list_type == list_type)
        
        if is_active is not None:
            query = query.filter(AMLSanctionList.is_active == is_active)
        
        if search_name:
            query = query.filter(
                AMLSanctionList.entity_name.ilike(f"%{search_name}%")
            )
        
        query = query.order_by(desc(AMLSanctionList.last_updated))
        
        return query.offset(skip).limit(limit).all()
    
    def update_sanction_list(
        self,
        updates: List[Dict[str, Any]],
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Bulk update sanction list
        Used for periodic updates from external sources
        """
        added = 0
        updated = 0
        deactivated = 0
        
        for entry in updates:
            existing = self.db.query(AMLSanctionList).filter(
                AMLSanctionList.tenant_id == self.tenant_id,
                AMLSanctionList.list_id == entry['list_id']
            ).first()
            
            if existing:
                # Update existing entry
                existing.entity_name = entry.get('entity_name', existing.entity_name)
                existing.is_active = entry.get('is_active', existing.is_active)
                existing.last_updated = datetime.utcnow()
                existing.updated_by = user_id
                updated += 1
            else:
                # Create new entry
                data = SanctionListCreate(**entry)
                self.create_sanction_list_entry(data, user_id)
                added += 1
        
        # Deactivate entries not in update
        if updates:
            list_ids = [e['list_id'] for e in updates]
            to_deactivate = self.db.query(AMLSanctionList).filter(
                AMLSanctionList.tenant_id == self.tenant_id,
                AMLSanctionList.is_active == True,
                ~AMLSanctionList.list_id.in_(list_ids)
            ).all()
            
            for entry in to_deactivate:
                entry.is_active = False
                entry.removal_date = date.today()
                entry.updated_by = user_id
                deactivated += 1
        
        self.db.commit()
        
        return {
            'added': added,
            'updated': updated,
            'deactivated': deactivated,
            'total_processed': len(updates)
        }
    
    # ========================================================================
    # SANCTION SCREENING
    # ========================================================================
    
    def create_screening(
        self,
        data: SanctionScreeningCreate,
        user_id: Optional[UUID] = None
    ) -> AMLSanctionScreening:
        """Create a new sanction screening"""
        screening_id = self._generate_screening_id()
        
        screening = AMLSanctionScreening(
            id=uuid4(),
            tenant_id=self.tenant_id,
            screening_id=screening_id,
            screening_date=datetime.utcnow(),
            customer_id=data.customer_id,
            customer_name=data.customer_name,
            screening_name=data.screening_name or data.customer_name,
            date_of_birth=data.date_of_birth,
            nationality=data.nationality,
            screening_type=data.screening_type,
            trigger_event=data.trigger_event,
            screening_status=ScreeningStatus.PENDING_REVIEW,
            is_match_found=False,
            risk_level=TransactionRiskLevel.CRITICAL,
            account_blocked=False,
            transaction_blocked=False,
            authorities_notified=False,
            created_by=user_id,
            updated_by=user_id
        )
        
        # Perform automated screening
        screening_result = self._perform_automated_screening(screening)
        
        if screening_result['match_found']:
            screening.is_match_found = True
            screening.match_type = screening_result['match_type']
            screening.match_score = screening_result['match_score']
            screening.matched_list_id = screening_result['matched_list_id']
            screening.matched_list_name = screening_result['matched_list_name']
            screening.match_details = screening_result['match_details']
            screening.screening_status = ScreeningStatus.POTENTIAL_MATCH
        else:
            screening.screening_status = ScreeningStatus.CLEAR
        
        # Calculate next review date
        if screening.is_match_found:
            screening.next_review_date = date.today() + timedelta(days=30)
        else:
            screening.next_review_date = date.today() + timedelta(days=365)
        
        self.db.add(screening)
        
        # Log screening
        self._log_audit(
            event_type='sanction_screening_created',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Created sanction screening {screening_id}",
            action_details={
                'customer_name': data.customer_name,
                'screening_type': data.screening_type,
                'match_found': screening.is_match_found
            }
        )
        
        self.db.commit()
        self.db.refresh(screening)
        
        return screening
    
    def _perform_automated_screening(
        self,
        screening: AMLSanctionScreening
    ) -> Dict[str, Any]:
        """
        Perform automated sanction screening
        """
        result = {
            'match_found': False,
            'match_type': None,
            'match_score': None,
            'matched_list_id': None,
            'matched_list_name': None,
            'match_details': {}
        }
        
        # Get active sanction lists
        sanctions = self.db.query(AMLSanctionList).filter(
            AMLSanctionList.tenant_id == self.tenant_id,
            AMLSanctionList.is_active == True
        ).all()
        
        best_match = None
        best_score = 0
        
        screening_name = screening.screening_name.lower()
        
        for sanction in sanctions:
            # Check exact match
            if screening_name == sanction.entity_name.lower():
                result['match_found'] = True
                result['match_type'] = 'exact'
                result['match_score'] = Decimal('100.0')
                result['matched_list_id'] = sanction.id
                result['matched_list_name'] = sanction.list_name
                result['match_details'] = {
                    'entity_name': sanction.entity_name,
                    'list_type': sanction.list_type,
                    'sanction_type': sanction.sanction_type,
                    'designation_date': sanction.designation_date.isoformat() if sanction.designation_date else None
                }
                return result
            
            # Check fuzzy match
            score = self._calculate_similarity(screening_name, sanction.entity_name.lower())
            if score > best_score:
                best_score = score
                best_match = sanction
            
            # Check aliases
            if sanction.aliases:
                for alias in sanction.aliases:
                    alias_score = self._calculate_similarity(screening_name, alias.lower())
                    if alias_score > best_score:
                        best_score = alias_score
                        best_match = sanction
        
        # If fuzzy match score is high enough (>85%), consider it a potential match
        if best_score >= 85:
            result['match_found'] = True
            result['match_type'] = 'fuzzy'
            result['match_score'] = Decimal(str(best_score))
            result['matched_list_id'] = best_match.id
            result['matched_list_name'] = best_match.list_name
            result['match_details'] = {
                'entity_name': best_match.entity_name,
                'list_type': best_match.list_type,
                'sanction_type': best_match.sanction_type,
                'similarity_score': best_score,
                'designation_date': best_match.designation_date.isoformat() if best_match.designation_date else None
            }
        
        return result
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings (0-100)"""
        return SequenceMatcher(None, str1, str2).ratio() * 100
    
    def get_screening(self, screening_id: UUID) -> Optional[AMLSanctionScreening]:
        """Get sanction screening by ID"""
        return self.db.query(AMLSanctionScreening).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id,
            AMLSanctionScreening.id == screening_id
        ).first()
    
    def list_screenings(
        self,
        customer_id: Optional[UUID] = None,
        screening_status: Optional[str] = None,
        is_match_found: Optional[bool] = None,
        screening_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AMLSanctionScreening]:
        """List sanction screenings with filters"""
        query = self.db.query(AMLSanctionScreening).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id
        )
        
        if customer_id:
            query = query.filter(AMLSanctionScreening.customer_id == customer_id)
        
        if screening_status:
            query = query.filter(AMLSanctionScreening.screening_status == screening_status)
        
        if is_match_found is not None:
            query = query.filter(AMLSanctionScreening.is_match_found == is_match_found)
        
        if screening_type:
            query = query.filter(AMLSanctionScreening.screening_type == screening_type)
        
        query = query.order_by(desc(AMLSanctionScreening.screening_date))
        
        return query.offset(skip).limit(limit).all()
    
    def update_screening(
        self,
        screening_id: UUID,
        data: SanctionScreeningUpdate,
        user_id: UUID
    ) -> Optional[AMLSanctionScreening]:
        """Update sanction screening result"""
        screening = self.get_screening(screening_id)
        
        if not screening:
            return None
        
        screening.screening_status = ScreeningStatus(data.screening_status)
        screening.is_match_found = data.is_match_found
        
        if data.match_type:
            screening.match_type = data.match_type
        
        if data.match_score is not None:
            screening.match_score = data.match_score
        
        if data.matched_list_id:
            screening.matched_list_id = data.matched_list_id
        
        if data.matched_list_name:
            screening.matched_list_name = data.matched_list_name
        
        if data.match_details:
            screening.match_details = data.match_details
        
        if data.decision:
            screening.decision = data.decision
        
        if data.decision_rationale:
            screening.decision_rationale = data.decision_rationale
        
        screening.account_blocked = data.account_blocked
        screening.transaction_blocked = data.transaction_blocked
        screening.authorities_notified = data.authorities_notified
        
        screening.reviewed_by = user_id
        screening.reviewed_at = datetime.utcnow()
        screening.updated_by = user_id
        screening.updated_at = datetime.utcnow()
        
        # Log update
        self._log_audit(
            event_type='sanction_screening_updated',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Updated sanction screening {screening.screening_id}",
            action_details={
                'decision': data.decision,
                'account_blocked': data.account_blocked,
                'authorities_notified': data.authorities_notified
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
    ) -> Optional[AMLSanctionScreening]:
        """Mark screening as false positive"""
        screening = self.get_screening(screening_id)
        
        if not screening:
            return None
        
        screening.screening_status = ScreeningStatus.FALSE_POSITIVE
        screening.decision = 'false_positive'
        screening.decision_rationale = reason
        screening.reviewed_by = user_id
        screening.reviewed_at = datetime.utcnow()
        screening.updated_by = user_id
        screening.updated_at = datetime.utcnow()
        
        # Log false positive
        self._log_audit(
            event_type='sanction_false_positive',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Marked {screening.screening_id} as false positive",
            action_details={'reason': reason}
        )
        
        self.db.commit()
        self.db.refresh(screening)
        
        return screening
    
    def confirm_match(
        self,
        screening_id: UUID,
        action_details: Dict[str, Any],
        user_id: UUID
    ) -> Optional[AMLSanctionScreening]:
        """Confirm sanction match and take action"""
        screening = self.get_screening(screening_id)
        
        if not screening:
            return None
        
        screening.screening_status = ScreeningStatus.CONFIRMED_MATCH
        screening.decision = 'true_positive'
        screening.account_blocked = action_details.get('block_account', True)
        screening.transaction_blocked = action_details.get('block_transactions', True)
        screening.authorities_notified = action_details.get('notify_authorities', True)
        screening.action_details = action_details
        screening.reviewed_by = user_id
        screening.reviewed_at = datetime.utcnow()
        screening.updated_by = user_id
        screening.updated_at = datetime.utcnow()
        
        # Log confirmation
        self._log_audit(
            event_type='sanction_match_confirmed',
            user_id=user_id,
            reference_id=str(screening.id),
            action=f"Confirmed sanction match for {screening.screening_id}",
            action_details=action_details
        )
        
        self.db.commit()
        self.db.refresh(screening)
        
        return screening
    
    def get_sanction_statistics(self) -> Dict[str, Any]:
        """Get sanction screening statistics"""
        total_screenings = self.db.query(AMLSanctionScreening).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id
        ).count()
        
        matches_found = self.db.query(AMLSanctionScreening).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id,
            AMLSanctionScreening.is_match_found == True
        ).count()
        
        confirmed_matches = self.db.query(AMLSanctionScreening).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id,
            AMLSanctionScreening.screening_status == ScreeningStatus.CONFIRMED_MATCH
        ).count()
        
        pending_review = self.db.query(AMLSanctionScreening).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id,
            AMLSanctionScreening.screening_status.in_([
                ScreeningStatus.PENDING_REVIEW,
                ScreeningStatus.POTENTIAL_MATCH
            ])
        ).count()
        
        accounts_blocked = self.db.query(AMLSanctionScreening).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id,
            AMLSanctionScreening.account_blocked == True
        ).count()
        
        # Active sanction lists
        active_lists = self.db.query(AMLSanctionList).filter(
            AMLSanctionList.tenant_id == self.tenant_id,
            AMLSanctionList.is_active == True
        ).count()
        
        return {
            'total_screenings': total_screenings,
            'matches_found': matches_found,
            'confirmed_matches': confirmed_matches,
            'pending_review': pending_review,
            'accounts_blocked': accounts_blocked,
            'active_sanction_lists': active_lists
        }
    
    def _generate_screening_id(self) -> str:
        """Generate unique screening ID"""
        prefix = "SAN"
        date_str = datetime.utcnow().strftime("%Y%m%d")
        
        count = self.db.query(func.count(AMLSanctionScreening.id)).filter(
            AMLSanctionScreening.tenant_id == self.tenant_id,
            func.date(AMLSanctionScreening.created_at) == date.today()
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
            reference_type='sanction_screening',
            reference_id=reference_id,
            action=action,
            action_details=action_details,
            result='success'
        )
        
        self.db.add(log)
