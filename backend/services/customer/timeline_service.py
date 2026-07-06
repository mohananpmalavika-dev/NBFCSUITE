"""
Customer Timeline Service
Service layer for customer activity history and timeline tracking
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta

from backend.shared.database.customer_models import (
    Customer, CustomerTimeline, ActivityType
)


class CustomerTimelineService:
    """Service for customer timeline operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def log_activity(
        self,
        customer_id: int,
        activity_type: ActivityType,
        title: str,
        description: Optional[str] = None,
        event_category: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_important: bool = False,
        is_visible_to_customer: bool = False
    ) -> CustomerTimeline:
        """
        Log a customer activity/event
        
        Args:
            customer_id: Customer ID
            activity_type: Type of activity
            title: Activity title
            description: Activity description
            event_category: Category (kyc, loan, payment, etc.)
            related_entity_type: Related entity type (loan, document, etc.)
            related_entity_id: Related entity ID
            old_value: Previous state (for change tracking)
            new_value: New state (for change tracking)
            metadata: Additional metadata
            is_important: Flag as important
            is_visible_to_customer: Show to customer
        
        Returns:
            CustomerTimeline record
        """
        
        # Calculate changes if both old and new values provided
        changes = None
        if old_value and new_value:
            changes = self._calculate_changes(old_value, new_value)
        
        # Get user info
        from backend.shared.database.models import User
        user_query = select(User).where(User.id == self.user_id)
        user_result = await self.db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        timeline = CustomerTimeline(
            tenant_id=self.tenant_id,
            customer_id=customer_id,
            activity_type=activity_type,
            title=title,
            description=description,
            event_category=event_category or self._infer_category(activity_type),
            event_source="api",
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
            performed_by=self.user_id,
            performed_by_name=user.full_name if user else None,
            performed_by_role=user.role if user else None,
            old_value=old_value,
            new_value=new_value,
            changes=changes,
            metadata=metadata,
            is_important=is_important,
            is_visible_to_customer=is_visible_to_customer,
            is_system_generated=False,
            created_by=self.user_id
        )
        
        self.db.add(timeline)
        await self.db.commit()
        await self.db.refresh(timeline)
        
        return timeline
    
    async def get_customer_timeline(
        self,
        customer_id: int,
        page: int = 1,
        page_size: int = 50,
        activity_types: Optional[List[ActivityType]] = None,
        event_category: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        important_only: bool = False
    ) -> Tuple[List[CustomerTimeline], int]:
        """
        Get customer timeline with filters
        
        Args:
            customer_id: Customer ID
            page: Page number
            page_size: Items per page
            activity_types: Filter by activity types
            event_category: Filter by category
            start_date: Start date filter
            end_date: End date filter
            important_only: Show only important events
        
        Returns:
            Tuple of (timeline items, total count)
        """
        
        # Base query
        query = select(CustomerTimeline).where(
            and_(
                CustomerTimeline.customer_id == customer_id,
                CustomerTimeline.tenant_id == self.tenant_id
            )
        )
        
        # Apply filters
        if activity_types:
            query = query.where(CustomerTimeline.activity_type.in_(activity_types))
        
        if event_category:
            query = query.where(CustomerTimeline.event_category == event_category)
        
        if start_date:
            query = query.where(CustomerTimeline.event_date >= start_date)
        
        if end_date:
            query = query.where(CustomerTimeline.event_date <= end_date)
        
        if important_only:
            query = query.where(CustomerTimeline.is_important == True)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(CustomerTimeline.event_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def get_recent_activities(
        self,
        customer_id: int,
        limit: int = 10
    ) -> List[CustomerTimeline]:
        """Get recent activities for customer"""
        
        query = select(CustomerTimeline).where(
            and_(
                CustomerTimeline.customer_id == customer_id,
                CustomerTimeline.tenant_id == self.tenant_id
            )
        ).order_by(CustomerTimeline.event_date.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_activity_summary(
        self,
        customer_id: int,
        days: int = 30
    ) -> Dict[str, int]:
        """
        Get activity summary for last N days
        
        Returns count by activity type
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        query = select(
            CustomerTimeline.activity_type,
            func.count(CustomerTimeline.id).label("count")
        ).where(
            and_(
                CustomerTimeline.customer_id == customer_id,
                CustomerTimeline.tenant_id == self.tenant_id,
                CustomerTimeline.event_date >= start_date
            )
        ).group_by(CustomerTimeline.activity_type)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return {str(row.activity_type): row.count for row in rows}
    
    async def search_timeline(
        self,
        customer_id: int,
        search_text: str,
        limit: int = 20
    ) -> List[CustomerTimeline]:
        """Search timeline by title or description"""
        
        search_term = f"%{search_text}%"
        
        query = select(CustomerTimeline).where(
            and_(
                CustomerTimeline.customer_id == customer_id,
                CustomerTimeline.tenant_id == self.tenant_id,
                or_(
                    CustomerTimeline.title.ilike(search_term),
                    CustomerTimeline.description.ilike(search_term)
                )
            )
        ).order_by(CustomerTimeline.event_date.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_as_important(self, timeline_id: int) -> Optional[CustomerTimeline]:
        """Mark timeline event as important"""
        
        query = select(CustomerTimeline).where(
            and_(
                CustomerTimeline.id == timeline_id,
                CustomerTimeline.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        timeline = result.scalar_one_or_none()
        
        if timeline:
            timeline.is_important = True
            timeline.updated_by = self.user_id
            timeline.updated_at = datetime.now()
            await self.db.commit()
            await self.db.refresh(timeline)
        
        return timeline
    
    async def add_note(
        self,
        customer_id: int,
        note: str,
        is_important: bool = False
    ) -> CustomerTimeline:
        """Add a manual note to customer timeline"""
        
        return await self.log_activity(
            customer_id=customer_id,
            activity_type=ActivityType.NOTE_ADDED,
            title="Note added",
            description=note,
            event_category="other",
            is_important=is_important,
            is_visible_to_customer=False
        )
    
    def _calculate_changes(
        self,
        old_value: Dict[str, Any],
        new_value: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Calculate differences between old and new values"""
        
        changes = {}
        
        # Find changed fields
        all_keys = set(old_value.keys()) | set(new_value.keys())
        
        for key in all_keys:
            old_val = old_value.get(key)
            new_val = new_value.get(key)
            
            if old_val != new_val:
                changes[key] = {
                    "old": old_val,
                    "new": new_val
                }
        
        return changes
    
    def _infer_category(self, activity_type: ActivityType) -> str:
        """Infer event category from activity type"""
        
        category_map = {
            # KYC events
            ActivityType.KYC_INITIATED: "kyc",
            ActivityType.KYC_COMPLETED: "kyc",
            ActivityType.KYC_REJECTED: "kyc",
            ActivityType.AADHAAR_VERIFIED: "kyc",
            ActivityType.PAN_VERIFIED: "kyc",
            ActivityType.VIDEO_KYC_COMPLETED: "kyc",
            ActivityType.BIOMETRIC_CAPTURED: "kyc",
            
            # Document events
            ActivityType.DOCUMENT_UPLOADED: "document",
            ActivityType.DOCUMENT_VERIFIED: "document",
            ActivityType.DOCUMENT_REJECTED: "document",
            ActivityType.DOCUMENT_EXPIRED: "document",
            
            # Bureau events
            ActivityType.CIBIL_PULLED: "bureau",
            ActivityType.BUREAU_REPORT_FETCHED: "bureau",
            ActivityType.CREDIT_SCORE_UPDATED: "bureau",
            ActivityType.RISK_RATING_CHANGED: "bureau",
            
            # Loan events
            ActivityType.LOAN_APPLICATION_SUBMITTED: "loan",
            ActivityType.LOAN_APPROVED: "loan",
            ActivityType.LOAN_REJECTED: "loan",
            ActivityType.LOAN_DISBURSED: "loan",
            ActivityType.LOAN_CLOSED: "loan",
            
            # Payment events
            ActivityType.PAYMENT_RECEIVED: "payment",
            ActivityType.PAYMENT_MISSED: "payment",
            ActivityType.EMI_BOUNCED: "payment",
            ActivityType.PREPAYMENT_DONE: "payment",
            ActivityType.FORECLOSURE_DONE: "payment",
            
            # Collection events
            ActivityType.COLLECTION_CALL: "collection",
            ActivityType.FIELD_VISIT: "collection",
            ActivityType.PAYMENT_PROMISE: "collection",
            ActivityType.LEGAL_NOTICE_SENT: "collection",
            
            # Communication events
            ActivityType.SMS_SENT: "communication",
            ActivityType.EMAIL_SENT: "communication",
            ActivityType.WHATSAPP_SENT: "communication",
            ActivityType.CALL_MADE: "communication",
        }
        
        return category_map.get(activity_type, "other")
