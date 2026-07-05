"""
Customer Family Service
Business logic for customer family member operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, date

from backend.shared.database.customer_models import CustomerFamily
from .schemas import CustomerFamilyCreate, CustomerFamilyUpdate


class CustomerFamilyService:
    """Service for customer family operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def create_family_member(self, data: CustomerFamilyCreate) -> CustomerFamily:
        """Add family member to customer"""
        
        # Calculate age from DOB
        age = self._calculate_age(data.date_of_birth) if data.date_of_birth else None
        
        family_member = CustomerFamily(
            tenant_id=self.tenant_id,
            customer_id=data.customer_id,
            relationship_type_id=data.relationship_type_id,
            name=data.name,
            date_of_birth=data.date_of_birth,
            age=age,
            gender=data.gender,
            mobile=data.mobile,
            occupation=data.occupation,
            monthly_income=data.monthly_income,
            is_dependent=data.is_dependent,
            is_emergency_contact=data.is_emergency_contact,
            is_nominee=data.is_nominee,
            nominee_percentage=data.nominee_percentage,
            created_by=self.user_id
        )
        
        self.db.add(family_member)
        await self.db.commit()
        await self.db.refresh(family_member)
        
        return family_member
    
    async def get_family_members(
        self, 
        customer_id: int,
        is_nominee: Optional[bool] = None,
        is_emergency_contact: Optional[bool] = None
    ) -> List[CustomerFamily]:
        """Get all family members for a customer"""
        
        query = select(CustomerFamily).where(
            and_(
                CustomerFamily.customer_id == customer_id,
                CustomerFamily.tenant_id == self.tenant_id,
                CustomerFamily.is_deleted == False
            )
        )
        
        if is_nominee is not None:
            query = query.where(CustomerFamily.is_nominee == is_nominee)
        
        if is_emergency_contact is not None:
            query = query.where(CustomerFamily.is_emergency_contact == is_emergency_contact)
        
        query = query.order_by(CustomerFamily.created_at)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_family_member(self, member_id: int) -> Optional[CustomerFamily]:
        """Get family member by ID"""
        query = select(CustomerFamily).where(
            and_(
                CustomerFamily.id == member_id,
                CustomerFamily.tenant_id == self.tenant_id,
                CustomerFamily.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_family_member(
        self, 
        member_id: int, 
        data: CustomerFamilyUpdate
    ) -> Optional[CustomerFamily]:
        """Update family member details"""
        member = await self.get_family_member(member_id)
        if not member:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        
        # Recalculate age if DOB changed
        if 'date_of_birth' in update_data and update_data['date_of_birth']:
            update_data['age'] = self._calculate_age(update_data['date_of_birth'])
        
        for field, value in update_data.items():
            setattr(member, field, value)
        
        member.updated_by = self.user_id
        member.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(member)
        
        return member
    
    async def delete_family_member(self, member_id: int) -> bool:
        """Soft delete family member"""
        member = await self.get_family_member(member_id)
        if not member:
            return False
        
        member.is_deleted = True
        member.updated_by = self.user_id
        member.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def validate_nominee_percentage(self, customer_id: int) -> dict:
        """Validate that nominee percentages add up to 100%"""
        members = await self.get_family_members(customer_id, is_nominee=True)
        
        total_percentage = sum(
            m.nominee_percentage for m in members if m.nominee_percentage
        )
        
        return {
            "is_valid": total_percentage == 100,
            "total_percentage": float(total_percentage),
            "nominees_count": len(members),
            "message": "Valid" if total_percentage == 100 else f"Total is {total_percentage}%, should be 100%"
        }
    
    def _calculate_age(self, dob: date) -> int:
        """Calculate age from date of birth"""
        today = date.today()
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        return age
