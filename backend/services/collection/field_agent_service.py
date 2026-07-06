"""
Field Agent Service
Manages field agents, territories, visits, and mobile app operations
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy import select, and_, or_, func, desc, extract
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.collection_models import (
    FieldAgent,
    Territory,
    FieldVisit,
    VisitTarget,
    VisitStatus,
    VisitDisposition,
    PaymentPromise,
    PromiseStatus,
    PromiseSource
)
from backend.shared.database.loan_models import LoanAccount
from backend.shared.database.customer_models import Customer


class FieldAgentService:
    """Service for field agent operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ========================================================================
    # TERRITORY MANAGEMENT
    # ========================================================================
    
    async def create_territory(
        self,
        territory_code: str,
        territory_name: str,
        state: Optional[str] = None,
        district: Optional[str] = None,
        city: Optional[str] = None,
        pincode_list: Optional[List[str]] = None,
        parent_territory_id: Optional[int] = None,
        branch_id: Optional[int] = None
    ) -> Territory:
        """Create new territory"""
        territory = Territory(
            tenant_id=self.tenant_id,
            territory_code=territory_code,
            territory_name=territory_name,
            state=state,
            district=district,
            city=city,
            pincode_list=pincode_list or [],
            parent_territory_id=parent_territory_id,
            branch_id=branch_id,
            created_by=self.user_id
        )
        
        self.db.add(territory)
        await self.db.commit()
        await self.db.refresh(territory)
        
        return territory
    
    async def get_territory(self, territory_id: int) -> Optional[Territory]:
        """Get territory by ID"""
        query = select(Territory).where(
            and_(
                Territory.id == territory_id,
                Territory.tenant_id == self.tenant_id,
                Territory.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    # ========================================================================
    # FIELD AGENT MANAGEMENT
    # ========================================================================
    
    async def create_agent(
        self,
        agent_code: str,
        full_name: str,
        mobile: str,
        territory_id: int,
        user_id: Optional[int] = None,
        email: Optional[str] = None,
        branch_id: Optional[int] = None,
        reporting_manager_id: Optional[int] = None,
        employment_type: str = "permanent",
        joining_date: Optional[date] = None,
        monthly_collection_target: Optional[Decimal] = None,
        monthly_visit_target: Optional[int] = None
    ) -> FieldAgent:
        """Create new field agent"""
        agent = FieldAgent(
            tenant_id=self.tenant_id,
            user_id=user_id,
            agent_code=agent_code,
            full_name=full_name,
            mobile=mobile,
            email=email,
            territory_id=territory_id,
            branch_id=branch_id,
            reporting_manager_id=reporting_manager_id,
            employment_type=employment_type,
            joining_date=joining_date or date.today(),
            monthly_collection_target=monthly_collection_target or Decimal("0"),
            monthly_visit_target=monthly_visit_target or 0,
            created_by=self.user_id
        )
        
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        
        return agent
    
    async def get_agent(self, agent_id: int) -> Optional[FieldAgent]:
        """Get agent by ID"""
        query = select(FieldAgent).where(
            and_(
                FieldAgent.id == agent_id,
                FieldAgent.tenant_id == self.tenant_id,
                FieldAgent.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_agent_by_user_id(self, user_id: int) -> Optional[FieldAgent]:
        """Get agent by user ID (for mobile login)"""
        query = select(FieldAgent).where(
            and_(
                FieldAgent.user_id == user_id,
                FieldAgent.tenant_id == self.tenant_id,
                FieldAgent.is_deleted == False,
                FieldAgent.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_agents(
        self,
        territory_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """List agents with filters"""
        conditions = [
            FieldAgent.tenant_id == self.tenant_id,
            FieldAgent.is_deleted == False
        ]
        
        if territory_id:
            conditions.append(FieldAgent.territory_id == territory_id)
        if is_active is not None:
            conditions.append(FieldAgent.is_active == is_active)
        
        count_query = select(func.count(FieldAgent.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        query = select(FieldAgent).where(and_(*conditions)).order_by(
            FieldAgent.full_name
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        agents = result.scalars().all()
        
        return {
            "agents": agents,
            "pagination": {
                "total": total,
                "skip": skip,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }
    
    # ========================================================================
    # VISIT MANAGEMENT
    # ========================================================================
    
    async def create_visit(
        self,
        loan_account_id: int,
        customer_id: int,
        agent_id: int,
        visit_date: date,
        scheduled_time: Optional[datetime] = None,
        visit_type: str = "routine"
    ) -> FieldVisit:
        """Schedule a field visit"""
        visit = FieldVisit(
            tenant_id=self.tenant_id,
            loan_account_id=loan_account_id,
            customer_id=customer_id,
            agent_id=agent_id,
            visit_date=visit_date,
            scheduled_time=scheduled_time,
            visit_type=visit_type,
            visit_status=VisitStatus.SCHEDULED
        )
        
        self.db.add(visit)
        await self.db.commit()
        await self.db.refresh(visit)
        
        return visit
    
    async def get_visit(self, visit_id: int) -> Optional[FieldVisit]:
        """Get visit by ID"""
        query = select(FieldVisit).where(
            and_(
                FieldVisit.id == visit_id,
                FieldVisit.tenant_id == self.tenant_id,
                FieldVisit.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_agent_visits(
        self,
        agent_id: int,
        visit_date: Optional[date] = None,
        status: Optional[VisitStatus] = None
    ) -> List[FieldVisit]:
        """Get visits for an agent (for mobile app)"""
        conditions = [
            FieldVisit.tenant_id == self.tenant_id,
            FieldVisit.agent_id == agent_id,
            FieldVisit.is_deleted == False
        ]
        
        if visit_date:
            conditions.append(FieldVisit.visit_date == visit_date)
        else:
            # Default to today's visits
            conditions.append(FieldVisit.visit_date == date.today())
        
        if status:
            conditions.append(FieldVisit.visit_status == status)
        
        query = select(FieldVisit).where(and_(*conditions)).order_by(
            FieldVisit.scheduled_time
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_visit(
        self,
        visit_id: int,
        visit_status: Optional[VisitStatus] = None,
        disposition: Optional[VisitDisposition] = None,
        amount_collected: Optional[Decimal] = None,
        payment_mode: Optional[str] = None,
        receipt_number: Optional[str] = None,
        location_lat: Optional[Decimal] = None,
        location_lng: Optional[Decimal] = None,
        visit_notes: Optional[str] = None,
        customer_remarks: Optional[str] = None,
        photo_urls: Optional[List[str]] = None,
        next_visit_date: Optional[date] = None,
        follow_up_required: bool = False
    ) -> Optional[FieldVisit]:
        """Update visit (from mobile app)"""
        visit = await self.get_visit(visit_id)
        if not visit:
            return None
        
        if visit_status:
            visit.visit_status = visit_status
            if visit_status == VisitStatus.COMPLETED:
                visit.actual_visit_time = datetime.now()
        
        if disposition:
            visit.disposition = disposition
        if amount_collected is not None:
            visit.amount_collected = amount_collected
        if payment_mode:
            visit.payment_mode = payment_mode
        if receipt_number:
            visit.receipt_number = receipt_number
        if location_lat and location_lng:
            visit.location_lat = location_lat
            visit.location_lng = location_lng
        if visit_notes:
            visit.visit_notes = visit_notes
        if customer_remarks:
            visit.customer_remarks = customer_remarks
        if photo_urls:
            visit.photo_urls = photo_urls
        if next_visit_date:
            visit.next_visit_date = next_visit_date
        
        visit.follow_up_required = follow_up_required
        visit.updated_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(visit)
        
        # Update agent performance
        if amount_collected and amount_collected > 0:
            await self._update_agent_collection(visit.agent_id, amount_collected)
        
        return visit
    
    async def allocate_visits_to_agent(
        self,
        agent_id: int,
        visit_date: date,
        max_visits: int = 20
    ) -> List[FieldVisit]:
        """Auto-allocate visits to agent based on territory and priority"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return []
        
        # Get overdue accounts in agent's territory
        # This would need customer address to pincode mapping
        # Simplified version - get high priority overdue accounts
        query = select(LoanAccount).where(
            and_(
                LoanAccount.tenant_id == self.tenant_id,
                LoanAccount.is_deleted == False,
                LoanAccount.status.in_(["overdue", "npa"]),
                LoanAccount.dpd > 30  # Priority for DPD > 30
            )
        ).order_by(desc(LoanAccount.dpd)).limit(max_visits)
        
        result = await self.db.execute(query)
        accounts = result.scalars().all()
        
        visits = []
        for account in accounts:
            # Check if visit already scheduled
            existing_visit_query = select(FieldVisit).where(
                and_(
                    FieldVisit.tenant_id == self.tenant_id,
                    FieldVisit.loan_account_id == account.id,
                    FieldVisit.visit_date == visit_date,
                    FieldVisit.is_deleted == False
                )
            )
            existing_result = await self.db.execute(existing_visit_query)
            if existing_result.scalar_one_or_none():
                continue
            
            visit = await self.create_visit(
                loan_account_id=account.id,
                customer_id=account.customer_id,
                agent_id=agent_id,
                visit_date=visit_date,
                visit_type="routine"
            )
            visits.append(visit)
        
        return visits
    
    async def _update_agent_collection(self, agent_id: int, amount: Decimal):
        """Update agent's total collection"""
        agent = await self.get_agent(agent_id)
        if agent:
            agent.total_collection_amount += amount
            agent.updated_at = datetime.now()
            await self.db.commit()
    
    # ========================================================================
    # TARGET MANAGEMENT
    # ========================================================================
    
    async def set_monthly_target(
        self,
        agent_id: int,
        month: int,
        year: int,
        collection_target: Decimal,
        visit_target: int
    ) -> VisitTarget:
        """Set monthly target for agent"""
        # Check if target already exists
        query = select(VisitTarget).where(
            and_(
                VisitTarget.tenant_id == self.tenant_id,
                VisitTarget.agent_id == agent_id,
                VisitTarget.month == month,
                VisitTarget.year == year,
                VisitTarget.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        target = result.scalar_one_or_none()
        
        if target:
            # Update existing
            target.target_collection_amount = collection_target
            target.target_visit_count = visit_target
            target.updated_at = datetime.now()
        else:
            # Create new
            target = VisitTarget(
                tenant_id=self.tenant_id,
                agent_id=agent_id,
                month=month,
                year=year,
                target_collection_amount=collection_target,
                target_visit_count=visit_target
            )
            self.db.add(target)
        
        await self.db.commit()
        await self.db.refresh(target)
        
        return target
    
    async def get_agent_performance(
        self,
        agent_id: int,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get agent performance metrics"""
        if not month:
            month = date.today().month
        if not year:
            year = date.today().year
        
        # Get target
        target_query = select(VisitTarget).where(
            and_(
                VisitTarget.tenant_id == self.tenant_id,
                VisitTarget.agent_id == agent_id,
                VisitTarget.month == month,
                VisitTarget.year == year,
                VisitTarget.is_deleted == False
            )
        )
        target_result = await self.db.execute(target_query)
        target = target_result.scalar_one_or_none()
        
        # Calculate achievement
        visit_query = select(
            func.count(FieldVisit.id).label("visit_count"),
            func.sum(FieldVisit.amount_collected).label("collection_amount")
        ).where(
            and_(
                FieldVisit.tenant_id == self.tenant_id,
                FieldVisit.agent_id == agent_id,
                extract('month', FieldVisit.visit_date) == month,
                extract('year', FieldVisit.visit_date) == year,
                FieldVisit.visit_status == VisitStatus.COMPLETED,
                FieldVisit.is_deleted == False
            )
        )
        visit_result = await self.db.execute(visit_query)
        achievement = visit_result.one()
        
        achieved_visits = achievement.visit_count or 0
        achieved_collection = achievement.collection_amount or Decimal("0")
        
        return {
            "agent_id": agent_id,
            "month": month,
            "year": year,
            "target_collection_amount": float(target.target_collection_amount) if target else 0,
            "achieved_collection_amount": float(achieved_collection),
            "collection_achievement_percentage": (
                float(achieved_collection / target.target_collection_amount * 100)
                if target and target.target_collection_amount > 0 else 0
            ),
            "target_visit_count": target.target_visit_count if target else 0,
            "achieved_visit_count": achieved_visits,
            "visit_achievement_percentage": (
                float(achieved_visits / target.target_visit_count * 100)
                if target and target.target_visit_count > 0 else 0
            )
        }
    
    # ========================================================================
    # MOBILE APP APIS
    # ========================================================================
    
    async def get_agent_dashboard(self, agent_id: int) -> Dict[str, Any]:
        """Get dashboard data for mobile app"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return {}
        
        today = date.today()
        
        # Today's visits
        today_visits = await self.get_agent_visits(agent_id, today)
        
        # Pending visits
        pending_visits = [v for v in today_visits if v.visit_status == VisitStatus.SCHEDULED]
        completed_visits = [v for v in today_visits if v.visit_status == VisitStatus.COMPLETED]
        
        # Today's collection
        today_collection = sum(v.amount_collected for v in completed_visits)
        
        # This month's performance
        performance = await self.get_agent_performance(agent_id, today.month, today.year)
        
        return {
            "agent": {
                "id": agent.id,
                "name": agent.full_name,
                "code": agent.agent_code,
                "mobile": agent.mobile
            },
            "today": {
                "date": today.isoformat(),
                "total_visits": len(today_visits),
                "pending_visits": len(pending_visits),
                "completed_visits": len(completed_visits),
                "collection_amount": float(today_collection)
            },
            "monthly_performance": performance,
            "upcoming_visits": [
                {
                    "id": v.id,
                    "loan_account_id": v.loan_account_id,
                    "customer_id": v.customer_id,
                    "scheduled_time": v.scheduled_time.isoformat() if v.scheduled_time else None,
                    "visit_type": v.visit_type,
                    "status": v.visit_status.value
                }
                for v in pending_visits[:10]  # Top 10 pending
            ]
        }
    
    async def record_payment_from_visit(
        self,
        visit_id: int,
        amount: Decimal,
        payment_mode: str,
        promise_amount: Optional[Decimal] = None,
        promise_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Record payment collected during visit"""
        visit = await self.get_visit(visit_id)
        if not visit:
            raise ValueError("Visit not found")
        
        # Update visit with payment
        visit.amount_collected = amount
        visit.payment_mode = payment_mode
        visit.disposition = VisitDisposition.PAID
        visit.visit_status = VisitStatus.COMPLETED
        visit.actual_visit_time = datetime.now()
        
        await self.db.commit()
        
        # Create payment promise if provided
        promise_id = None
        if promise_amount and promise_date:
            promise = PaymentPromise(
                tenant_id=self.tenant_id,
                loan_account_id=visit.loan_account_id,
                customer_id=visit.customer_id,
                promise_amount=promise_amount,
                promise_date=promise_date,
                promised_on_date=date.today(),
                promised_by=PromiseSource.FIELD_VISIT,
                agent_id=visit.agent_id,
                field_visit_id=visit.id,
                promise_status=PromiseStatus.PENDING,
                recorded_by_user_id=self.user_id
            )
            self.db.add(promise)
            await self.db.commit()
            await self.db.refresh(promise)
            promise_id = promise.id
        
        return {
            "visit_id": visit.id,
            "payment_recorded": True,
            "amount": float(amount),
            "promise_id": promise_id
        }
