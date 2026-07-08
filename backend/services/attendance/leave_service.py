"""
Leave Management Service Layer
Business logic for leave policies, applications, and balance management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, between
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, date, timedelta
import calendar

from backend.shared.database.attendance_models import (
    LeavePolicyMaster, EmployeeLeaveBalance, LeaveApplication, LeaveEncashment,
    LeaveType, LeaveStatus, LeavePeriod
)
from .schemas import (
    LeavePolicyCreate, LeavePolicyUpdate, LeaveApplicationCreate,
    LeaveApplicationUpdate, LeaveEncashmentRequest
)


class LeavePolicyService:
    """Service for leave policy operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_policy(self, data: LeavePolicyCreate) -> LeavePolicyMaster:
        """Create new leave policy"""
        policy = LeavePolicyMaster(
            tenant_id=self.tenant_id,
            policy_code=data.policy_code,
            policy_name=data.policy_name,
            leave_type=data.leave_type,
            annual_quota=data.annual_quota,
            max_consecutive_days=data.max_consecutive_days,
            min_notice_days=data.min_notice_days,
            max_carry_forward=data.max_carry_forward,
            is_accrual_based=data.is_accrual_based,
            accrual_frequency=data.accrual_frequency,
            accrual_rate=data.accrual_rate,
            applicable_after_days=data.applicable_after_days,
            applicable_gender=data.applicable_gender,
            allow_half_day=data.allow_half_day,
            allow_negative_balance=data.allow_negative_balance,
            require_document=data.require_document,
            require_document_after_days=data.require_document_after_days,
            include_weekends=data.include_weekends,
            include_holidays=data.include_holidays,
            is_encashable=data.is_encashable,
            encashment_min_balance=data.encashment_min_balance,
            encashment_percentage=data.encashment_percentage,
            effective_from=data.effective_from,
            effective_to=data.effective_to,
            description=data.description,
            rules=str(data.rules) if data.rules else None,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy
    
    async def get_policy(self, policy_id: str) -> Optional[LeavePolicyMaster]:
        """Get leave policy by ID"""
        query = select(LeavePolicyMaster).where(
            and_(
                LeavePolicyMaster.id == policy_id,
                LeavePolicyMaster.tenant_id == self.tenant_id,
                LeavePolicyMaster.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_policies(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        leave_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[LeavePolicyMaster], int]:
        """Get paginated leave policies"""
        query = select(LeavePolicyMaster).where(
            and_(
                LeavePolicyMaster.tenant_id == self.tenant_id,
                LeavePolicyMaster.is_deleted == False
            )
        )
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    LeavePolicyMaster.policy_name.ilike(search_term),
                    LeavePolicyMaster.policy_code.ilike(search_term)
                )
            )
        
        if leave_type:
            query = query.where(LeavePolicyMaster.leave_type == leave_type)
        
        if is_active is not None:
            query = query.where(LeavePolicyMaster.is_active == is_active)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(LeavePolicyMaster.leave_type, LeavePolicyMaster.policy_name)
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        policies = result.scalars().all()
        
        return policies, total
    
    async def update_policy(self, policy_id: str, data: LeavePolicyUpdate) -> LeavePolicyMaster:
        """Update leave policy"""
        policy = await self.get_policy(policy_id)
        if not policy:
            raise ValueError("Leave policy not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "rules" and value:
                value = str(value)
            setattr(policy, field, value)
        
        policy.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(policy)
        return policy
    
    async def delete_policy(self, policy_id: str) -> bool:
        """Soft delete leave policy"""
        policy = await self.get_policy(policy_id)
        if not policy:
            raise ValueError("Leave policy not found")
        
        policy.is_deleted = True
        policy.deleted_at = datetime.utcnow()
        
        await self.db.commit()
        return True


class LeaveBalanceService:
    """Service for leave balance operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def get_employee_balance(
        self, employee_id: str, financial_year: str
    ) -> List[EmployeeLeaveBalance]:
        """Get employee's leave balance for financial year"""
        query = select(EmployeeLeaveBalance).where(
            and_(
                EmployeeLeaveBalance.employee_id == employee_id,
                EmployeeLeaveBalance.financial_year == financial_year,
                EmployeeLeaveBalance.tenant_id == self.tenant_id,
                EmployeeLeaveBalance.is_deleted == False
            )
        ).options(selectinload(EmployeeLeaveBalance.leave_policy))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_balance_by_leave_type(
        self, employee_id: str, leave_type: LeaveType, financial_year: str
    ) -> Optional[EmployeeLeaveBalance]:
        """Get balance for specific leave type"""
        query = select(EmployeeLeaveBalance).where(
            and_(
                EmployeeLeaveBalance.employee_id == employee_id,
                EmployeeLeaveBalance.leave_type == leave_type,
                EmployeeLeaveBalance.financial_year == financial_year,
                EmployeeLeaveBalance.tenant_id == self.tenant_id,
                EmployeeLeaveBalance.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def initialize_employee_balance(
        self, employee_id: str, policy_id: str, financial_year: str
    ) -> EmployeeLeaveBalance:
        """Initialize leave balance for employee"""
        # Get policy details
        policy_query = select(LeavePolicyMaster).where(
            LeavePolicyMaster.id == policy_id
        )
        policy_result = await self.db.execute(policy_query)
        policy = policy_result.scalar_one_or_none()
        
        if not policy:
            raise ValueError("Leave policy not found")
        
        # Check if balance already exists
        existing = await self.get_balance_by_leave_type(
            employee_id, policy.leave_type, financial_year
        )
        if existing:
            return existing
        
        balance = EmployeeLeaveBalance(
            tenant_id=self.tenant_id,
            employee_id=employee_id,
            leave_policy_id=policy_id,
            leave_type=policy.leave_type,
            financial_year=financial_year,
            opening_balance=policy.annual_quota,
            current_balance=policy.annual_quota
        )
        
        self.db.add(balance)
        await self.db.commit()
        await self.db.refresh(balance)
        return balance
    
    async def accrue_leave(
        self, employee_id: str, leave_type: LeaveType, financial_year: str, accrual_amount: float
    ) -> EmployeeLeaveBalance:
        """Accrue leave for employee"""
        balance = await self.get_balance_by_leave_type(employee_id, leave_type, financial_year)
        if not balance:
            raise ValueError("Leave balance not found")
        
        balance.accrued += accrual_amount
        balance.current_balance += accrual_amount
        balance.last_accrual_date = date.today()
        balance.last_updated = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(balance)
        return balance
    
    async def deduct_leave(
        self, employee_id: str, leave_type: LeaveType, financial_year: str, days: float
    ) -> EmployeeLeaveBalance:
        """Deduct leave from balance"""
        balance = await self.get_balance_by_leave_type(employee_id, leave_type, financial_year)
        if not balance:
            raise ValueError("Leave balance not found")
        
        if balance.current_balance < days:
            # Check if negative balance is allowed
            policy = await self.db.get(LeavePolicyMaster, balance.leave_policy_id)
            if not policy or not policy.allow_negative_balance:
                raise ValueError("Insufficient leave balance")
        
        balance.availed += days
        balance.current_balance -= days
        balance.last_updated = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(balance)
        return balance
    
    async def restore_leave(
        self, employee_id: str, leave_type: LeaveType, financial_year: str, days: float
    ) -> EmployeeLeaveBalance:
        """Restore leave to balance (for cancelled applications)"""
        balance = await self.get_balance_by_leave_type(employee_id, leave_type, financial_year)
        if not balance:
            raise ValueError("Leave balance not found")
        
        balance.availed -= days
        balance.current_balance += days
        balance.last_updated = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(balance)
        return balance


class LeaveApplicationService:
    """Service for leave application operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_application_code(self) -> str:
        """Generate unique application code: LV-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(LeaveApplication.id)).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.application_code.like(f"LV-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"LV-{year_month}-{sequence}"
    
    async def create_application(self, data: LeaveApplicationCreate) -> LeaveApplication:
        """Create new leave application"""
        application_code = await self.generate_application_code()
        
        # Calculate total days
        total_days = await self._calculate_leave_days(
            data.from_date, data.to_date, data.from_period, data.to_period,
            data.leave_policy_id
        )
        
        # Get current balance
        balance_service = LeaveBalanceService(self.db, self.tenant_id, self.user_id)
        financial_year = self._get_financial_year(data.from_date)
        balance = await balance_service.get_balance_by_leave_type(
            data.employee_id, data.leave_type, financial_year
        )
        
        if not balance:
            raise ValueError("Leave balance not initialized for this employee")
        
        # Check if sufficient balance
        if balance.current_balance < total_days:
            policy = await self.db.get(LeavePolicyMaster, data.leave_policy_id)
            if not policy or not policy.allow_negative_balance:
                raise ValueError(f"Insufficient leave balance. Available: {balance.current_balance}, Requested: {total_days}")
        
        application = LeaveApplication(
            tenant_id=self.tenant_id,
            application_code=application_code,
            employee_id=data.employee_id,
            leave_policy_id=data.leave_policy_id,
            leave_type=data.leave_type,
            from_date=data.from_date,
            to_date=data.to_date,
            from_period=data.from_period,
            to_period=data.to_period,
            total_days=total_days,
            reason=data.reason,
            contact_during_leave=data.contact_during_leave,
            address_during_leave=data.address_during_leave,
            supporting_documents=str(data.supporting_documents) if data.supporting_documents else None,
            status=LeaveStatus.DRAFT,
            balance_before=balance.current_balance,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(application)
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def get_application(self, application_id: str) -> Optional[LeaveApplication]:
        """Get leave application by ID"""
        query = select(LeaveApplication).where(
            and_(
                LeaveApplication.id == application_id,
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.is_deleted == False
            )
        ).options(
            selectinload(LeaveApplication.employee),
            selectinload(LeaveApplication.leave_policy)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_applications(
        self,
        page: int = 1,
        page_size: int = 20,
        employee_id: Optional[str] = None,
        status: Optional[str] = None,
        leave_type: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Tuple[List[LeaveApplication], int]:
        """Get paginated leave applications"""
        query = select(LeaveApplication).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.is_deleted == False
            )
        ).options(
            selectinload(LeaveApplication.employee),
            selectinload(LeaveApplication.leave_policy)
        )
        
        if employee_id:
            query = query.where(LeaveApplication.employee_id == employee_id)
        
        if status:
            query = query.where(LeaveApplication.status == status)
        
        if leave_type:
            query = query.where(LeaveApplication.leave_type == leave_type)
        
        if from_date and to_date:
            query = query.where(
                or_(
                    between(LeaveApplication.from_date, from_date, to_date),
                    between(LeaveApplication.to_date, from_date, to_date)
                )
            )
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(LeaveApplication.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        applications = result.scalars().all()
        
        return applications, total
    
    async def update_application(
        self, application_id: str, data: LeaveApplicationUpdate
    ) -> LeaveApplication:
        """Update leave application (only in DRAFT status)"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Leave application not found")
        
        if application.status != LeaveStatus.DRAFT:
            raise ValueError("Can only update applications in DRAFT status")
        
        # Recalculate total days if dates changed
        if data.from_date or data.to_date or data.from_period or data.to_period:
            from_date = data.from_date or application.from_date
            to_date = data.to_date or application.to_date
            from_period = data.from_period or application.from_period
            to_period = data.to_period or application.to_period
            
            total_days = await self._calculate_leave_days(
                from_date, to_date, from_period, to_period,
                application.leave_policy_id
            )
            application.total_days = total_days
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "supporting_documents" and value:
                value = str(value)
            setattr(application, field, value)
        
        application.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def submit_application(self, application_id: str) -> LeaveApplication:
        """Submit leave application for approval"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Leave application not found")
        
        if application.status != LeaveStatus.DRAFT:
            raise ValueError("Can only submit applications in DRAFT status")
        
        application.status = LeaveStatus.PENDING
        application.applied_date = date.today()
        application.updated_by = self.user_id
        
        # Update pending balance
        balance_service = LeaveBalanceService(self.db, self.tenant_id, self.user_id)
        financial_year = self._get_financial_year(application.from_date)
        balance = await balance_service.get_balance_by_leave_type(
            application.employee_id, application.leave_type, financial_year
        )
        if balance:
            balance.pending_approval += application.total_days
        
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def approve_application(
        self, application_id: str, approver_level: str, remarks: Optional[str] = None
    ) -> LeaveApplication:
        """Approve leave application"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Leave application not found")
        
        if application.status != LeaveStatus.PENDING:
            raise ValueError("Can only approve applications in PENDING status")
        
        # Update approval chain
        if approver_level == "REPORTING_MANAGER":
            application.reporting_manager_id = self.user_id
            application.reporting_manager_status = "APPROVED"
            application.reporting_manager_remarks = remarks
            application.reporting_manager_date = datetime.utcnow()
        elif approver_level == "HR":
            application.hr_approver_id = self.user_id
            application.hr_approver_status = "APPROVED"
            application.hr_approver_remarks = remarks
            application.hr_approver_date = datetime.utcnow()
        elif approver_level == "FINAL":
            application.final_approver_id = self.user_id
            application.final_approver_status = "APPROVED"
            application.final_approver_remarks = remarks
            application.final_approver_date = datetime.utcnow()
            
            # Final approval - deduct from balance
            application.status = LeaveStatus.APPROVED
            
            balance_service = LeaveBalanceService(self.db, self.tenant_id, self.user_id)
            financial_year = self._get_financial_year(application.from_date)
            
            # Deduct from balance
            balance = await balance_service.deduct_leave(
                application.employee_id,
                application.leave_type,
                financial_year,
                application.total_days
            )
            
            # Update pending balance
            balance.pending_approval -= application.total_days
            application.balance_after = balance.current_balance
        
        application.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def reject_application(
        self, application_id: str, rejection_reason: str
    ) -> LeaveApplication:
        """Reject leave application"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Leave application not found")
        
        if application.status != LeaveStatus.PENDING:
            raise ValueError("Can only reject applications in PENDING status")
        
        application.status = LeaveStatus.REJECTED
        application.rejection_reason = rejection_reason
        application.updated_by = self.user_id
        
        # Remove from pending balance
        balance_service = LeaveBalanceService(self.db, self.tenant_id, self.user_id)
        financial_year = self._get_financial_year(application.from_date)
        balance = await balance_service.get_balance_by_leave_type(
            application.employee_id, application.leave_type, financial_year
        )
        if balance:
            balance.pending_approval -= application.total_days
        
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def cancel_application(
        self, application_id: str, cancellation_reason: str
    ) -> LeaveApplication:
        """Cancel leave application"""
        application = await self.get_application(application_id)
        if not application:
            raise ValueError("Leave application not found")
        
        if application.status not in [LeaveStatus.PENDING, LeaveStatus.APPROVED]:
            raise ValueError("Can only cancel PENDING or APPROVED applications")
        
        # Restore balance if already approved
        if application.status == LeaveStatus.APPROVED:
            balance_service = LeaveBalanceService(self.db, self.tenant_id, self.user_id)
            financial_year = self._get_financial_year(application.from_date)
            await balance_service.restore_leave(
                application.employee_id,
                application.leave_type,
                financial_year,
                application.total_days
            )
        else:
            # Remove from pending if still pending
            balance_service = LeaveBalanceService(self.db, self.tenant_id, self.user_id)
            financial_year = self._get_financial_year(application.from_date)
            balance = await balance_service.get_balance_by_leave_type(
                application.employee_id, application.leave_type, financial_year
            )
            if balance:
                balance.pending_approval -= application.total_days
        
        application.status = LeaveStatus.CANCELLED
        application.is_cancelled = True
        application.cancelled_by = self.user_id
        application.cancellation_reason = cancellation_reason
        application.cancelled_at = datetime.utcnow()
        application.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def _calculate_leave_days(
        self, from_date: date, to_date: date,
        from_period: LeavePeriod, to_period: LeavePeriod,
        policy_id: str
    ) -> float:
        """Calculate total leave days"""
        # Get policy to check weekend/holiday inclusion
        policy = await self.db.get(LeavePolicyMaster, policy_id)
        if not policy:
            raise ValueError("Leave policy not found")
        
        total_days = 0.0
        current_date = from_date
        
        while current_date <= to_date:
            # Check if weekend
            is_weekend = current_date.weekday() in [5, 6]  # Saturday, Sunday
            
            # Check if holiday (TODO: integrate with holiday calendar)
            is_holiday = False
            
            # Skip weekends if not included
            if is_weekend and not policy.include_weekends:
                current_date += timedelta(days=1)
                continue
            
            # Skip holidays if not included
            if is_holiday and not policy.include_holidays:
                current_date += timedelta(days=1)
                continue
            
            # Count the day
            if current_date == from_date and from_period != LeavePeriod.FULL_DAY:
                total_days += 0.5
            elif current_date == to_date and to_period != LeavePeriod.FULL_DAY:
                total_days += 0.5
            else:
                total_days += 1.0
            
            current_date += timedelta(days=1)
        
        return total_days
    
    def _get_financial_year(self, ref_date: date) -> str:
        """Get financial year for given date (Apr-Mar)"""
        if ref_date.month >= 4:
            return f"{ref_date.year}-{str(ref_date.year + 1)[2:]}"
        else:
            return f"{ref_date.year - 1}-{str(ref_date.year)[2:]}"
    
    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get leave dashboard statistics"""
        # Total applications
        total_query = select(func.count(LeaveApplication.id)).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # By status
        status_query = select(
            LeaveApplication.status,
            func.count(LeaveApplication.id)
        ).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.is_deleted == False
            )
        ).group_by(LeaveApplication.status)
        
        status_result = await self.db.execute(status_query)
        status_counts = dict(status_result.all())
        
        # On leave today
        today = date.today()
        today_query = select(func.count(LeaveApplication.id)).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.status == LeaveStatus.APPROVED,
                LeaveApplication.from_date <= today,
                LeaveApplication.to_date >= today,
                LeaveApplication.is_deleted == False
            )
        )
        today_result = await self.db.execute(today_query)
        on_leave_today = today_result.scalar() or 0
        
        # Upcoming leaves
        upcoming_query = select(func.count(LeaveApplication.id)).where(
            and_(
                LeaveApplication.tenant_id == self.tenant_id,
                LeaveApplication.status == LeaveStatus.APPROVED,
                LeaveApplication.from_date > today,
                LeaveApplication.is_deleted == False
            )
        )
        upcoming_result = await self.db.execute(upcoming_query)
        upcoming = upcoming_result.scalar() or 0
        
        return {
            "total_applications": total,
            "pending_approval": status_counts.get(LeaveStatus.PENDING, 0),
            "approved": status_counts.get(LeaveStatus.APPROVED, 0),
            "rejected": status_counts.get(LeaveStatus.REJECTED, 0),
            "on_leave_today": on_leave_today,
            "upcoming_leaves": upcoming
        }
