"""
Locker Waiting List Service

Handles waiting list queue management including:
- Priority-based queue management
- Automatic position calculation
- Offer management and tracking
- Auto-allocation when lockers become available
- Customer notification management
- Queue analytics and reporting
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

from backend.shared.database.locker_models import (
    LockerWaitingList,
    LockerApplication,
    LockerMaster,
    LockerAllocation,
    Customer
)
from backend.services.locker.schemas import (
    LockerWaitingListCreate,
    LockerWaitingListUpdate,
    LockerWaitingListResponse,
    WaitingListOfferRequest,
    WaitingListOfferResponse,
    WaitingListFilter,
    WaitingListStatus,
    LockerSize,
    LockerStatus,
    WaitingListAnalytics,
    WaitingListStatistics
)
from backend.shared.utils import generate_reference_number


class WaitingListService:
    """Service for managing locker waiting list"""
    
    def __init__(self, db: Session, tenant_id: str, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def add_to_waiting_list(
        self,
        data: LockerWaitingListCreate
    ) -> LockerWaitingList:
        """
        Add customer to waiting list with priority calculation
        """
        # Generate waiting list ID
        waiting_list_id = generate_reference_number("WL")
        
        # Calculate priority score
        priority_score = self._calculate_priority_score(data)
        
        # Calculate position in queue
        position = await self._calculate_queue_position(
            data.branch_id,
            data.locker_size_requested,
            priority_score
        )
        
        # Estimate waiting time
        estimated_wait_days = await self._estimate_waiting_time(
            data.branch_id,
            data.locker_size_requested,
            position
        )
        
        # Create waiting list entry
        waiting_entry = LockerWaitingList(
            waiting_list_id=waiting_list_id,
            tenant_id=self.tenant_id,
            application_id=data.application_id,
            customer_id=data.customer_id,
            branch_id=data.branch_id,
            added_date=data.added_date,
            locker_size_requested=data.locker_size_requested,
            position_in_queue=position,
            priority_score=priority_score,
            base_priority=data.base_priority,
            existing_customer_bonus=data.existing_customer_bonus,
            deposit_size_bonus=data.deposit_size_bonus,
            senior_citizen_bonus=data.senior_citizen_bonus,
            staff_bonus=data.staff_bonus,
            waiting_time_bonus=data.waiting_time_bonus,
            status=WaitingListStatus.ACTIVE,
            auto_allocate_enabled=data.auto_allocate_enabled,
            accept_alternate_size=data.accept_alternate_size,
            max_rent_willing=data.max_rent_willing,
            preferred_contact_method=data.preferred_contact_method,
            preferred_contact_time=data.preferred_contact_time,
            contact_mobile=data.contact_mobile,
            contact_email=data.contact_email,
            estimated_wait_days=estimated_wait_days,
            special_requirements=data.special_requirements,
            remarks=data.remarks,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(waiting_entry)
        self.db.commit()
        self.db.refresh(waiting_entry)
        
        # Recalculate positions for all entries
        await self._recalculate_all_positions(data.branch_id, data.locker_size_requested)
        
        return waiting_entry
    
    def _calculate_priority_score(self, data: LockerWaitingListCreate) -> int:
        """
        Calculate total priority score from all components
        """
        return (
            data.base_priority +
            data.existing_customer_bonus +
            data.deposit_size_bonus +
            data.senior_citizen_bonus +
            data.staff_bonus +
            data.waiting_time_bonus
        )
    
    async def _calculate_queue_position(
        self,
        branch_id: uuid.UUID,
        locker_size: LockerSize,
        priority_score: int
    ) -> int:
        """
        Calculate position in queue based on priority score
        Higher priority = Lower position number (1 is first)
        """
        # Count entries with higher priority
        higher_priority_count = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.branch_id == branch_id,
                LockerWaitingList.locker_size_requested == locker_size,
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.priority_score > priority_score,
                LockerWaitingList.is_deleted == False
            )
        ).count()
        
        # Position is count + 1
        return higher_priority_count + 1
    
    async def _recalculate_all_positions(
        self,
        branch_id: uuid.UUID,
        locker_size: LockerSize
    ) -> None:
        """
        Recalculate positions for all active entries in queue
        """
        entries = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.branch_id == branch_id,
                LockerWaitingList.locker_size_requested == locker_size,
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.is_deleted == False
            )
        ).order_by(
            desc(LockerWaitingList.priority_score),
            asc(LockerWaitingList.added_date)
        ).all()
        
        for idx, entry in enumerate(entries, start=1):
            entry.position_in_queue = idx
        
        self.db.commit()
    
    async def _estimate_waiting_time(
        self,
        branch_id: uuid.UUID,
        locker_size: LockerSize,
        position: int
    ) -> int:
        """
        Estimate waiting time in days based on historical turnover rate
        """
        # Calculate average turnover (allocations that ended in last 12 months)
        twelve_months_ago = date.today() - timedelta(days=365)
        
        ended_allocations = self.db.query(LockerAllocation).join(
            LockerMaster
        ).filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerMaster.branch_id == branch_id,
                LockerMaster.locker_size == locker_size,
                LockerAllocation.closure_date >= twelve_months_ago,
                LockerAllocation.is_deleted == False
            )
        ).count()
        
        if ended_allocations > 0:
            # Average turnovers per month
            turnovers_per_month = ended_allocations / 12
            
            # Estimate days to reach position
            if turnovers_per_month > 0:
                months_to_wait = position / turnovers_per_month
                return int(months_to_wait * 30)
        
        # Default estimate: 30 days per position
        return position * 30
    
    async def get_waiting_entry(
        self,
        entry_id: uuid.UUID
    ) -> Optional[LockerWaitingList]:
        """Get waiting list entry by ID"""
        return self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.id == entry_id,
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.is_deleted == False
            )
        ).first()
    
    async def get_entry_by_application(
        self,
        application_id: uuid.UUID
    ) -> Optional[LockerWaitingList]:
        """Get waiting list entry by application ID"""
        return self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.application_id == application_id,
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.is_deleted == False
            )
        ).first()
    
    async def list_waiting_entries(
        self,
        filters: WaitingListFilter,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[LockerWaitingList], int]:
        """List waiting list entries with filters"""
        query = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.is_deleted == False
            )
        )
        
        # Apply filters
        if filters.branch_id:
            query = query.filter(LockerWaitingList.branch_id == filters.branch_id)
        
        if filters.locker_size_requested:
            query = query.filter(
                LockerWaitingList.locker_size_requested == filters.locker_size_requested
            )
        
        if filters.status:
            query = query.filter(LockerWaitingList.status == filters.status)
        
        if filters.min_priority_score:
            query = query.filter(
                LockerWaitingList.priority_score >= filters.min_priority_score
            )
        
        # Get total count
        total = query.count()
        
        # Order by position (priority)
        query = query.order_by(
            asc(LockerWaitingList.position_in_queue)
        )
        
        # Pagination
        entries = query.offset(skip).limit(limit).all()
        
        return entries, total
    
    async def update_waiting_entry(
        self,
        entry_id: uuid.UUID,
        data: LockerWaitingListUpdate
    ) -> Optional[LockerWaitingList]:
        """Update waiting list entry"""
        entry = await self.get_waiting_entry(entry_id)
        if not entry:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)
        
        entry.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    async def make_offer(
        self,
        entry_id: uuid.UUID,
        offer: WaitingListOfferRequest
    ) -> Optional[LockerWaitingList]:
        """
        Make locker offer to waiting list customer
        """
        entry = await self.get_waiting_entry(entry_id)
        if not entry:
            return None
        
        if entry.status != WaitingListStatus.ACTIVE:
            raise ValueError("Entry must be in active status to make offer")
        
        # Verify locker is available
        locker = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.id == offer.locker_id,
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.status == LockerStatus.AVAILABLE,
                LockerMaster.is_available == True,
                LockerMaster.is_deleted == False
            )
        ).first()
        
        if not locker:
            raise ValueError("Locker is not available")
        
        # Check if locker matches size requirement or alternate
        if not entry.accept_alternate_size:
            if locker.locker_size != entry.locker_size_requested:
                raise ValueError("Locker size doesn't match customer preference")
        
        # Check rent limit if specified
        if entry.max_rent_willing:
            if locker.annual_rent > entry.max_rent_willing:
                raise ValueError("Locker rent exceeds customer's willing amount")
        
        # Update entry with offer
        entry.locker_offered_id = offer.locker_id
        entry.offer_made_date = date.today()
        entry.offer_valid_till = date.today() + timedelta(days=offer.offer_valid_days)
        entry.status = WaitingListStatus.NOTIFIED
        entry.notification_sent = True
        entry.notification_sent_date = date.today()
        entry.notification_method = offer.notification_method
        entry.response_deadline = entry.offer_valid_till
        entry.updated_by = self.user_id
        
        # Block locker temporarily
        locker.status = LockerStatus.BLOCKED
        locker.special_notes = f"Offered to waiting list customer (WL: {entry.waiting_list_id})"
        locker.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(entry)
        
        # TODO: Send notification via email/SMS
        
        return entry
    
    async def record_customer_response(
        self,
        entry_id: uuid.UUID,
        response: WaitingListOfferResponse
    ) -> Optional[LockerWaitingList]:
        """
        Record customer response to locker offer
        """
        entry = await self.get_waiting_entry(entry_id)
        if not entry:
            return None
        
        if entry.status != WaitingListStatus.NOTIFIED:
            raise ValueError("No active offer found for this entry")
        
        entry.customer_response = "accepted" if response.accepted else "declined"
        entry.customer_response_date = response.response_date
        
        if response.accepted:
            # Customer accepted the offer
            entry.status = WaitingListStatus.ACCEPTED
            # Keep locker blocked for allocation process
        else:
            # Customer declined the offer
            entry.status = WaitingListStatus.DECLINED
            entry.offer_declined_reason = response.declined_reason
            
            # Release the locker back to available
            if entry.locker_offered_id:
                locker = self.db.query(LockerMaster).filter(
                    LockerMaster.id == entry.locker_offered_id
                ).first()
                if locker:
                    locker.status = LockerStatus.AVAILABLE
                    locker.special_notes = None
                    locker.updated_by = self.user_id
            
            # Reactivate entry for future offers
            entry.status = WaitingListStatus.ACTIVE
            entry.locker_offered_id = None
            entry.offer_made_date = None
            entry.offer_valid_till = None
        
        entry.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(entry)
        
        return entry
    
    async def process_allocation(
        self,
        entry_id: uuid.UUID,
        allocation_id: uuid.UUID
    ) -> Optional[LockerWaitingList]:
        """
        Mark entry as allocated after allocation is completed
        """
        entry = await self.get_waiting_entry(entry_id)
        if not entry:
            return None
        
        entry.allocated = True
        entry.allocation_id = allocation_id
        entry.allocation_date = date.today()
        entry.status = WaitingListStatus.ALLOCATED
        entry.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(entry)
        
        # Recalculate positions after removal
        await self._recalculate_all_positions(
            entry.branch_id,
            entry.locker_size_requested
        )
        
        return entry
    
    async def remove_from_waiting_list(
        self,
        entry_id: uuid.UUID,
        reason: str
    ) -> Optional[LockerWaitingList]:
        """
        Remove customer from waiting list
        """
        entry = await self.get_waiting_entry(entry_id)
        if not entry:
            return None
        
        entry.status = WaitingListStatus.CANCELLED
        entry.removed_date = date.today()
        entry.removal_reason = reason
        entry.updated_by = self.user_id
        
        # Release offered locker if any
        if entry.locker_offered_id and entry.status == WaitingListStatus.NOTIFIED:
            locker = self.db.query(LockerMaster).filter(
                LockerMaster.id == entry.locker_offered_id
            ).first()
            if locker:
                locker.status = LockerStatus.AVAILABLE
                locker.special_notes = None
                locker.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(entry)
        
        # Recalculate positions
        await self._recalculate_all_positions(
            entry.branch_id,
            entry.locker_size_requested
        )
        
        return entry
    
    async def check_expired_offers(self) -> List[LockerWaitingList]:
        """
        Check and process expired offers
        """
        expired = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.status == WaitingListStatus.NOTIFIED,
                LockerWaitingList.offer_valid_till < date.today(),
                LockerWaitingList.customer_response.is_(None),
                LockerWaitingList.is_deleted == False
            )
        ).all()
        
        for entry in expired:
            # Mark as no response
            entry.customer_response = "no_response"
            entry.status = WaitingListStatus.EXPIRED
            entry.updated_by = self.user_id
            
            # Release the locker
            if entry.locker_offered_id:
                locker = self.db.query(LockerMaster).filter(
                    LockerMaster.id == entry.locker_offered_id
                ).first()
                if locker:
                    locker.status = LockerStatus.AVAILABLE
                    locker.special_notes = None
                    locker.updated_by = self.user_id
        
        if expired:
            self.db.commit()
        
        return expired
    
    async def auto_allocate_available_locker(
        self,
        locker_id: uuid.UUID
    ) -> Optional[LockerWaitingList]:
        """
        Automatically allocate a newly available locker to waiting list
        """
        locker = self.db.query(LockerMaster).filter(
            and_(
                LockerMaster.id == locker_id,
                LockerMaster.tenant_id == self.tenant_id,
                LockerMaster.status == LockerStatus.AVAILABLE,
                LockerMaster.is_deleted == False
            )
        ).first()
        
        if not locker:
            return None
        
        # Find highest priority waiting customer for this locker
        waiting_entry = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.branch_id == locker.branch_id,
                or_(
                    LockerWaitingList.locker_size_requested == locker.locker_size,
                    and_(
                        LockerWaitingList.accept_alternate_size == True,
                        LockerWaitingList.locker_size_requested.in_([
                            LockerSize.SMALL, LockerSize.MEDIUM,
                            LockerSize.LARGE, LockerSize.EXTRA_LARGE
                        ])
                    )
                ),
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.auto_allocate_enabled == True,
                or_(
                    LockerWaitingList.max_rent_willing.is_(None),
                    LockerWaitingList.max_rent_willing >= locker.annual_rent
                ),
                LockerWaitingList.is_deleted == False
            )
        ).order_by(
            asc(LockerWaitingList.position_in_queue)
        ).first()
        
        if waiting_entry:
            # Make automatic offer
            offer = WaitingListOfferRequest(
                locker_id=locker_id,
                offer_valid_days=7,
                notification_method=waiting_entry.preferred_contact_method
            )
            return await self.make_offer(waiting_entry.id, offer)
        
        return None
    
    async def get_next_in_queue(
        self,
        branch_id: uuid.UUID,
        locker_size: LockerSize
    ) -> Optional[LockerWaitingList]:
        """
        Get next customer in queue for specific branch and size
        """
        return self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.branch_id == branch_id,
                LockerWaitingList.locker_size_requested == locker_size,
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.is_deleted == False
            )
        ).order_by(
            asc(LockerWaitingList.position_in_queue)
        ).first()
    
    async def get_customer_waiting_entries(
        self,
        customer_id: uuid.UUID
    ) -> List[LockerWaitingList]:
        """Get all waiting list entries for a customer"""
        return self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.customer_id == customer_id,
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.is_deleted == False
            )
        ).order_by(desc(LockerWaitingList.added_date)).all()
    
    async def update_priority_scores(self) -> int:
        """
        Update priority scores for all active entries (adds waiting time bonus)
        Run this periodically (e.g., monthly)
        """
        active_entries = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.is_deleted == False
            )
        ).all()
        
        updated_count = 0
        
        for entry in active_entries:
            # Calculate waiting time in months
            waiting_days = (date.today() - entry.added_date).days
            waiting_months = waiting_days // 30
            
            # Add 2 points per month of waiting (max 20 points)
            new_waiting_bonus = min(waiting_months * 2, 20)
            
            if new_waiting_bonus != entry.waiting_time_bonus:
                entry.waiting_time_bonus = new_waiting_bonus
                entry.priority_score = (
                    entry.base_priority +
                    entry.existing_customer_bonus +
                    entry.deposit_size_bonus +
                    entry.senior_citizen_bonus +
                    entry.staff_bonus +
                    new_waiting_bonus
                )
                entry.updated_by = self.user_id
                updated_count += 1
        
        if updated_count > 0:
            self.db.commit()
            
            # Recalculate positions for all branches and sizes
            branches_sizes = self.db.query(
                LockerWaitingList.branch_id,
                LockerWaitingList.locker_size_requested
            ).filter(
                and_(
                    LockerWaitingList.tenant_id == self.tenant_id,
                    LockerWaitingList.status == WaitingListStatus.ACTIVE,
                    LockerWaitingList.is_deleted == False
                )
            ).distinct().all()
            
            for branch_id, locker_size in branches_sizes:
                await self._recalculate_all_positions(branch_id, locker_size)
        
        return updated_count
    
    async def get_analytics(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> WaitingListAnalytics:
        """Get waiting list analytics"""
        query = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerWaitingList.branch_id == branch_id)
        
        # Total waiting
        total_waiting = query.filter(
            LockerWaitingList.status == WaitingListStatus.ACTIVE
        ).count()
        
        # By size
        by_size = {}
        size_counts = query.filter(
            LockerWaitingList.status == WaitingListStatus.ACTIVE
        ).with_entities(
            LockerWaitingList.locker_size_requested,
            func.count(LockerWaitingList.id)
        ).group_by(LockerWaitingList.locker_size_requested).all()
        
        for size, count in size_counts:
            by_size[size] = count
        
        # By branch
        by_branch = {}
        if not branch_id:
            branch_counts = query.filter(
                LockerWaitingList.status == WaitingListStatus.ACTIVE
            ).with_entities(
                LockerWaitingList.branch_id,
                func.count(LockerWaitingList.id)
            ).group_by(LockerWaitingList.branch_id).all()
            
            for b_id, count in branch_counts:
                by_branch[str(b_id)] = count
        
        # Average wait time
        active_entries = query.filter(
            LockerWaitingList.status == WaitingListStatus.ACTIVE
        ).all()
        
        if active_entries:
            total_wait_days = sum([
                (date.today() - entry.added_date).days
                for entry in active_entries
            ])
            avg_wait = total_wait_days // len(active_entries)
            
            longest_wait = max([
                (date.today() - entry.added_date).days
                for entry in active_entries
            ])
        else:
            avg_wait = 0
            longest_wait = 0
        
        # Offers tracking
        offers_made = query.filter(
            LockerWaitingList.offer_made_date.isnot(None)
        ).count()
        
        offers_accepted = query.filter(
            LockerWaitingList.customer_response == "accepted"
        ).count()
        
        offers_declined = query.filter(
            LockerWaitingList.customer_response == "declined"
        ).count()
        
        return WaitingListAnalytics(
            total_waiting=total_waiting,
            by_size=by_size,
            by_branch=by_branch,
            average_wait_days=avg_wait,
            longest_wait_days=longest_wait,
            offers_made=offers_made,
            offers_accepted=offers_accepted,
            offers_declined=offers_declined
        )
    
    async def get_statistics(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> WaitingListStatistics:
        """Get detailed waiting list statistics"""
        query = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerWaitingList.branch_id == branch_id)
        
        total_waiting = query.count()
        
        # By size
        by_size = {}
        size_counts = query.with_entities(
            LockerWaitingList.locker_size_requested,
            func.count(LockerWaitingList.id)
        ).group_by(LockerWaitingList.locker_size_requested).all()
        
        for size, count in size_counts:
            by_size[size] = count
        
        # Average wait days
        entries = query.all()
        if entries:
            avg_wait = sum([(date.today() - e.added_date).days for e in entries]) // len(entries)
            
            # Longest waiting customer
            longest = max(entries, key=lambda e: (date.today() - e.added_date).days)
            longest_wait_customer = {
                "waiting_list_id": longest.waiting_list_id,
                "customer_id": str(longest.customer_id),
                "waiting_days": (date.today() - longest.added_date).days,
                "position": longest.position_in_queue,
                "size_requested": longest.locker_size_requested
            }
        else:
            avg_wait = 0
            longest_wait_customer = None
        
        # Expected allocations in next 30 days
        # Based on average turnover rate
        expected_allocations = await self._estimate_allocations_next_30_days(branch_id)
        
        return WaitingListStatistics(
            total_waiting=total_waiting,
            by_size=by_size,
            average_wait_days=avg_wait,
            longest_wait_customer=longest_wait_customer,
            expected_allocations_30_days=expected_allocations
        )
    
    async def _estimate_allocations_next_30_days(
        self,
        branch_id: Optional[uuid.UUID] = None
    ) -> int:
        """Estimate how many allocations expected in next 30 days"""
        # Based on historical turnover in last 90 days
        ninety_days_ago = date.today() - timedelta(days=90)
        
        query = self.db.query(LockerAllocation).join(LockerMaster)
        
        if branch_id:
            query = query.filter(LockerMaster.branch_id == branch_id)
        
        recent_closures = query.filter(
            and_(
                LockerAllocation.tenant_id == self.tenant_id,
                LockerAllocation.closure_date >= ninety_days_ago,
                LockerAllocation.is_deleted == False
            )
        ).count()
        
        # Average per month * 1 month
        monthly_avg = (recent_closures / 3) if recent_closures > 0 else 1
        
        return int(monthly_avg)
    
    async def send_reminder_notification(
        self,
        entry_id: uuid.UUID
    ) -> bool:
        """Send reminder to customer about their waiting list position"""
        entry = await self.get_waiting_entry(entry_id)
        if not entry:
            return False
        
        # Update notification tracking
        entry.notification_sent = True
        entry.notification_sent_date = date.today()
        
        self.db.commit()
        
        # TODO: Integrate with notification service
        return True
    
    async def bulk_notify_customers(
        self,
        branch_id: Optional[uuid.UUID] = None,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """Send notifications to top N customers in queue"""
        query = self.db.query(LockerWaitingList).filter(
            and_(
                LockerWaitingList.tenant_id == self.tenant_id,
                LockerWaitingList.status == WaitingListStatus.ACTIVE,
                LockerWaitingList.is_deleted == False
            )
        )
        
        if branch_id:
            query = query.filter(LockerWaitingList.branch_id == branch_id)
        
        top_entries = query.order_by(
            asc(LockerWaitingList.position_in_queue)
        ).limit(top_n).all()
        
        successful = 0
        failed = 0
        
        for entry in top_entries:
            try:
                result = await self.send_reminder_notification(entry.id)
                if result:
                    successful += 1
                else:
                    failed += 1
            except Exception:
                failed += 1
        
        return {
            "total": len(top_entries),
            "successful": successful,
            "failed": failed
        }
