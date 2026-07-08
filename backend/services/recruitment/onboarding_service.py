"""
Onboarding Service Layer
Business logic for onboarding operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date

from backend.shared.database.recruitment_models import (
    Onboarding, OnboardingStatus, BackgroundVerification
)
from .schemas import OnboardingCreate, OnboardingUpdate


class OnboardingService:
    """Service for onboarding operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_onboarding_code(self) -> str:
        """Generate unique onboarding code: ONB-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(Onboarding.id)).where(
            and_(
                Onboarding.tenant_id == self.tenant_id,
                Onboarding.onboarding_code.like(f"ONB-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"ONB-{year_month}-{sequence}"
    
    def _calculate_completion_percentage(self, onboarding: Onboarding) -> int:
        """Calculate onboarding completion percentage"""
        total_items = 9  # Number of checklist items
        completed = 0
        
        if onboarding.pre_joining_completed:
            completed += 1
        if onboarding.joining_day_completed:
            completed += 1
        if onboarding.first_week_completed:
            completed += 1
        if onboarding.id_card_issued:
            completed += 1
        if onboarding.email_account_created:
            completed += 1
        if onboarding.laptop_issued:
            completed += 1
        if onboarding.access_cards_issued:
            completed += 1
        if onboarding.induction_completed:
            completed += 1
        if onboarding.documents_verified:
            completed += 1
        
        return int((completed / total_items) * 100)
    
    async def create_onboarding(self, data: OnboardingCreate) -> Onboarding:
        """Create new onboarding record"""
        onboarding_code = await self.generate_onboarding_code()
        
        # Default checklists
        pre_joining_checklist = {
            "tasks": [
                {"id": 1, "title": "Submit documents", "completed": False},
                {"id": 2, "title": "Background verification", "completed": False},
                {"id": 3, "title": "Medical examination", "completed": False}
            ]
        }
        
        joining_day_checklist = {
            "tasks": [
                {"id": 1, "title": "Welcome & orientation", "completed": False},
                {"id": 2, "title": "ID card issuance", "completed": False},
                {"id": 3, "title": "Email account setup", "completed": False},
                {"id": 4, "title": "Laptop/device issuance", "completed": False}
            ]
        }
        
        first_week_checklist = {
            "tasks": [
                {"id": 1, "title": "Department introduction", "completed": False},
                {"id": 2, "title": "System access setup", "completed": False},
                {"id": 3, "title": "Policy training", "completed": False},
                {"id": 4, "title": "Meet buddy/mentor", "completed": False}
            ]
        }
        
        onboarding = Onboarding(
            tenant_id=self.tenant_id,
            onboarding_code=onboarding_code,
            application_id=data.application_id,
            joining_date=data.joining_date,
            offer_date=data.offer_date,
            offer_accepted_date=data.offer_accepted_date,
            buddy_employee_id=data.buddy_employee_id,
            pre_joining_checklist=pre_joining_checklist,
            joining_day_checklist=joining_day_checklist,
            first_week_checklist=first_week_checklist,
            status=OnboardingStatus.NOT_STARTED,
            completion_percentage=0,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(onboarding)
        await self.db.commit()
        await self.db.refresh(onboarding)
        
        return onboarding
    
    async def get_onboarding(self, onboarding_id: str) -> Optional[Onboarding]:
        """Get onboarding by ID"""
        query = select(Onboarding).where(
            and_(
                Onboarding.id == onboarding_id,
                Onboarding.tenant_id == self.tenant_id,
                Onboarding.is_deleted == False
            )
        ).options(
            selectinload(Onboarding.application),
            selectinload(Onboarding.employee),
            selectinload(Onboarding.buddy),
            selectinload(Onboarding.verifications)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_onboardings(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> Tuple[List[Onboarding], int]:
        """Get paginated list of onboardings"""
        query = select(Onboarding).where(
            and_(
                Onboarding.tenant_id == self.tenant_id,
                Onboarding.is_deleted == False
            )
        ).options(
            selectinload(Onboarding.application),
            selectinload(Onboarding.buddy)
        )
        
        if status:
            query = query.where(Onboarding.status == status)
        
        if from_date:
            query = query.where(Onboarding.joining_date >= from_date)
        
        if to_date:
            query = query.where(Onboarding.joining_date <= to_date)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(desc(Onboarding.joining_date))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        onboardings = result.scalars().all()
        
        return onboardings, total
    
    async def update_onboarding(
        self, onboarding_id: str, data: OnboardingUpdate
    ) -> Onboarding:
        """Update onboarding"""
        onboarding = await self.get_onboarding(onboarding_id)
        if not onboarding:
            raise ValueError("Onboarding not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(onboarding, field, value)
        
        # Recalculate completion percentage
        onboarding.completion_percentage = self._calculate_completion_percentage(onboarding)
        
        # Update status if all completed
        if onboarding.completion_percentage == 100:
            onboarding.status = OnboardingStatus.COMPLETED
            onboarding.onboarding_completed_date = date.today()
        elif onboarding.completion_percentage > 0:
            onboarding.status = OnboardingStatus.IN_PROGRESS
        
        onboarding.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(onboarding)
        
        return onboarding
    
    async def link_employee(
        self, onboarding_id: str, employee_id: str
    ) -> Onboarding:
        """Link created employee to onboarding"""
        onboarding = await self.get_onboarding(onboarding_id)
        if not onboarding:
            raise ValueError("Onboarding not found")
        
        onboarding.employee_id = employee_id
        onboarding.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(onboarding)
        
        return onboarding


class BackgroundVerificationService:
    """Service for background verification operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: str, user_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_verification_code(self) -> str:
        """Generate unique verification code: BGV-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        count_query = select(func.count(BackgroundVerification.id)).where(
            and_(
                BackgroundVerification.tenant_id == self.tenant_id,
                BackgroundVerification.verification_code.like(f"BGV-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        sequence = str(count + 1).zfill(4)
        return f"BGV-{year_month}-{sequence}"
    
    async def create_verification(self, data) -> BackgroundVerification:
        """Create new background verification"""
        verification_code = await self.generate_verification_code()
        
        verification = BackgroundVerification(
            tenant_id=self.tenant_id,
            verification_code=verification_code,
            onboarding_id=data.onboarding_id,
            verification_type=data.verification_type,
            verification_agency=data.verification_agency,
            expected_completion_date=data.expected_completion_date,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(verification)
        await self.db.commit()
        await self.db.refresh(verification)
        
        return verification
    
    async def get_verification(self, verification_id: str) -> Optional[BackgroundVerification]:
        """Get verification by ID"""
        query = select(BackgroundVerification).where(
            and_(
                BackgroundVerification.id == verification_id,
                BackgroundVerification.tenant_id == self.tenant_id,
                BackgroundVerification.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_verification(self, verification_id: str, data) -> BackgroundVerification:
        """Update verification"""
        verification = await self.get_verification(verification_id)
        if not verification:
            raise ValueError("Verification not found")
        
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(verification, field, value)
        
        # Set initiated date if moving to in progress
        if data.status == "in_progress" and not verification.initiated_date:
            verification.initiated_date = date.today()
        
        verification.updated_by = self.user_id
        
        await self.db.commit()
        await self.db.refresh(verification)
        
        return verification
