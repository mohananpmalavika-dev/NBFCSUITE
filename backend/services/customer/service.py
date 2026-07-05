"""
Customer Management Service Layer
Business logic for customer operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date
import random
import string

from backend.shared.database.customer_models import (
    Customer, CustomerKYC, CustomerDocument, CustomerFamily,
    CustomerBankAccount, CustomerReference, KYCStatus, RiskRating
)
from .schemas import (
    CustomerCreate, CustomerUpdate, CustomerListItem,
    CustomerDashboardStats
)


class CustomerService:
    """Service for customer operations"""
    
    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    async def generate_customer_code(self) -> str:
        """Generate unique customer code: CUS-YYYYMM-XXXX"""
        year_month = datetime.now().strftime("%Y%m")
        
        # Get count of customers this month
        count_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.customer_code.like(f"CUS-{year_month}-%")
            )
        )
        result = await self.db.execute(count_query)
        count = result.scalar() or 0
        
        # Generate code
        sequence = str(count + 1).zfill(4)
        return f"CUS-{year_month}-{sequence}"
    
    async def create_customer(self, data: CustomerCreate) -> Customer:
        """Create new customer with auto-generated code"""
        
        # Generate customer code
        customer_code = await self.generate_customer_code()
        
        # Calculate full name
        full_name = self._build_full_name(
            data.first_name, data.middle_name, data.last_name, data.business_name
        )
        
        # Calculate age from DOB
        age = self._calculate_age(data.date_of_birth) if data.date_of_birth else None
        
        # Create customer
        customer = Customer(
            tenant_id=self.tenant_id,
            customer_code=customer_code,
            customer_type=data.customer_type,
            first_name=data.first_name,
            middle_name=data.middle_name,
            last_name=data.last_name,
            full_name=full_name,
            business_name=data.business_name,
            email=data.email,
            mobile=data.mobile,
            alternate_mobile=data.alternate_mobile,
            pan_number=data.pan_number,
            aadhaar_number=data.aadhaar_number,
            date_of_birth=data.date_of_birth,
            age=age,
            gender=data.gender,
            marital_status=data.marital_status,
            father_name=data.father_name,
            mother_name=data.mother_name,
            kyc_status=KYCStatus.PENDING,
            risk_rating=RiskRating.MEDIUM,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        
        # Create empty KYC record
        await self._create_kyc_record(customer.id)
        
        return customer
    
    async def _create_kyc_record(self, customer_id: int):
        """Create initial KYC record for customer"""
        kyc = CustomerKYC(
            tenant_id=self.tenant_id,
            customer_id=customer_id,
            overall_kyc_status=KYCStatus.PENDING,
            kyc_completion_percentage=0,
            created_by=self.user_id
        )
        self.db.add(kyc)
        await self.db.commit()
    
    async def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID with relationships"""
        query = select(Customer).where(
            and_(
                Customer.id == customer_id,
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False
            )
        ).options(
            selectinload(Customer.documents),
            selectinload(Customer.family_members),
            selectinload(Customer.bank_accounts),
            selectinload(Customer.kyc_details)
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_customer_by_code(self, customer_code: str) -> Optional[Customer]:
        """Get customer by customer code"""
        query = select(Customer).where(
            and_(
                Customer.customer_code == customer_code,
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_customers(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        kyc_status: Optional[KYCStatus] = None,
        risk_rating: Optional[RiskRating] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[Customer], int]:
        """Get paginated list of customers with filters"""
        
        # Base query
        query = select(Customer).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False
            )
        )
        
        # Apply filters
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Customer.full_name.ilike(search_term),
                    Customer.customer_code.ilike(search_term),
                    Customer.mobile.like(search_term),
                    Customer.email.ilike(search_term),
                    Customer.pan_number.ilike(search_term)
                )
            )
        
        if kyc_status:
            query = query.where(Customer.kyc_status == kyc_status)
        
        if risk_rating:
            query = query.where(Customer.risk_rating == risk_rating)
        
        if is_active is not None:
            query = query.where(Customer.is_active == is_active)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        query = query.order_by(Customer.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        customers = result.scalars().all()
        
        return customers, total
    
    async def update_customer(
        self,
        customer_id: int,
        data: CustomerUpdate
    ) -> Optional[Customer]:
        """Update customer details"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return None
        
        # Update fields
        update_data = data.dict(exclude_unset=True)
        
        # Recalculate full name if name fields changed
        if any(k in update_data for k in ['first_name', 'middle_name', 'last_name']):
            full_name = self._build_full_name(
                update_data.get('first_name', customer.first_name),
                update_data.get('middle_name', customer.middle_name),
                update_data.get('last_name', customer.last_name),
                customer.business_name
            )
            update_data['full_name'] = full_name
        
        # Recalculate age if DOB changed
        if 'date_of_birth' in update_data:
            update_data['age'] = self._calculate_age(update_data['date_of_birth'])
        
        # Update fields
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        customer.updated_by = self.user_id
        customer.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(customer)
        
        return customer
    
    async def delete_customer(self, customer_id: int) -> bool:
        """Soft delete customer"""
        customer = await self.get_customer(customer_id)
        if not customer:
            return False
        
        customer.is_deleted = True
        customer.is_active = False
        customer.updated_by = self.user_id
        customer.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def search_customers(
        self,
        mobile: Optional[str] = None,
        pan: Optional[str] = None,
        aadhaar: Optional[str] = None
    ) -> List[Customer]:
        """Search customers by mobile, PAN, or Aadhaar"""
        conditions = [
            Customer.tenant_id == self.tenant_id,
            Customer.is_deleted == False
        ]
        
        if mobile:
            conditions.append(Customer.mobile == mobile)
        if pan:
            conditions.append(Customer.pan_number == pan.upper())
        if aadhaar:
            conditions.append(Customer.aadhaar_number == aadhaar)
        
        query = select(Customer).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_dashboard_stats(self) -> CustomerDashboardStats:
        """Get customer dashboard statistics"""
        
        # Total customers
        total_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False
            )
        )
        total_result = await self.db.execute(total_query)
        total_customers = total_result.scalar() or 0
        
        # Active customers
        active_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False,
                Customer.is_active == True
            )
        )
        active_result = await self.db.execute(active_query)
        active_customers = active_result.scalar() or 0
        
        # KYC pending
        kyc_pending_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False,
                Customer.kyc_status == KYCStatus.PENDING
            )
        )
        kyc_pending_result = await self.db.execute(kyc_pending_query)
        kyc_pending = kyc_pending_result.scalar() or 0
        
        # KYC completed
        kyc_completed_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False,
                Customer.kyc_status == KYCStatus.COMPLETED
            )
        )
        kyc_completed_result = await self.db.execute(kyc_completed_query)
        kyc_completed = kyc_completed_result.scalar() or 0
        
        # High risk customers
        high_risk_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False,
                Customer.risk_rating.in_([RiskRating.HIGH, RiskRating.VERY_HIGH])
            )
        )
        high_risk_result = await self.db.execute(high_risk_query)
        high_risk_customers = high_risk_result.scalar() or 0
        
        # Blacklisted customers
        blacklisted_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False,
                Customer.is_blacklisted == True
            )
        )
        blacklisted_result = await self.db.execute(blacklisted_query)
        blacklisted_customers = blacklisted_result.scalar() or 0
        
        # New this month
        first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_month_query = select(func.count(Customer.id)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False,
                Customer.created_at >= first_day_of_month
            )
        )
        new_month_result = await self.db.execute(new_month_query)
        new_this_month = new_month_result.scalar() or 0
        
        # Average CIBIL score
        avg_cibil_query = select(func.avg(Customer.cibil_score)).where(
            and_(
                Customer.tenant_id == self.tenant_id,
                Customer.is_deleted == False,
                Customer.cibil_score.isnot(None)
            )
        )
        avg_cibil_result = await self.db.execute(avg_cibil_query)
        avg_cibil = avg_cibil_result.scalar()
        avg_cibil_score = int(avg_cibil) if avg_cibil else None
        
        return CustomerDashboardStats(
            total_customers=total_customers,
            active_customers=active_customers,
            kyc_pending=kyc_pending,
            kyc_completed=kyc_completed,
            high_risk_customers=high_risk_customers,
            blacklisted_customers=blacklisted_customers,
            new_this_month=new_this_month,
            avg_cibil_score=avg_cibil_score
        )
    
    def _build_full_name(
        self,
        first_name: Optional[str],
        middle_name: Optional[str],
        last_name: Optional[str],
        business_name: Optional[str]
    ) -> str:
        """Build full name from name components"""
        if business_name:
            return business_name
        
        parts = []
        if first_name:
            parts.append(first_name)
        if middle_name:
            parts.append(middle_name)
        if last_name:
            parts.append(last_name)
        
        return " ".join(parts) if parts else "Unknown"
    
    def _calculate_age(self, dob: date) -> int:
        """Calculate age from date of birth"""
        today = date.today()
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        return age
