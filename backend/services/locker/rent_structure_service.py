"""
Locker Rent Structure Service

Handles rent calculation, pricing, and structure management including:
- Dynamic rent calculation based on size, location, customer category
- GST calculation
- Discount application
- Late payment penalty calculation
- Rent structure versioning
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from dateutil.relativedelta import relativedelta
import uuid

from backend.shared.database.locker_models import LockerRentStructure, LockerAllocation
from .schemas import (
    LockerRentStructureCreate, LockerRentStructureUpdate, LockerRentStructureResponse,
    RentCalculationRequest, RentCalculationResponse,
    LockerSize, CustomerCategory, RentFrequency
)


class RentStructureService:
    """Service for managing locker rent structures and calculations"""
    
    def __init__(self, db: Session, tenant_id: uuid.UUID, user_id: uuid.UUID):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== RENT STRUCTURE MANAGEMENT ====================
    
    async def create_rent_structure(
        self,
        structure_data: LockerRentStructureCreate
    ) -> LockerRentStructure:
        """Create a new rent structure"""
        # Generate structure ID
        rent_structure_id = f"RS{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Check for existing active structure with same parameters
        existing = self.db.query(LockerRentStructure).filter(
            and_(
                LockerRentStructure.tenant_id == self.tenant_id,
                LockerRentStructure.locker_size == structure_data.locker_size.value,
                LockerRentStructure.customer_category == structure_data.customer_category.value,
                LockerRentStructure.is_active == True,
                LockerRentStructure.is_deleted == False
            )
        ).first()
        
        # If branch-specific, check branch match
        if structure_data.branch_id and existing and existing.branch_id == structure_data.branch_id:
            # Deactivate old structure
            existing.is_active = False
            existing.effective_to = date.today()
        
        structure = LockerRentStructure(
            tenant_id=self.tenant_id,
            rent_structure_id=rent_structure_id,
            **structure_data.dict(exclude_unset=True),
            version_number=1,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(structure)
        self.db.commit()
        self.db.refresh(structure)
        
        return structure
    
    async def get_rent_structure(self, structure_id: uuid.UUID) -> Optional[LockerRentStructure]:
        """Get rent structure by ID"""
        return self.db.query(LockerRentStructure).filter(
            and_(
                LockerRentStructure.id == structure_id,
                LockerRentStructure.tenant_id == self.tenant_id,
                LockerRentStructure.is_deleted == False
            )
        ).first()
    
    async def get_active_rent_structure(
        self,
        locker_size: LockerSize,
        customer_category: CustomerCategory = CustomerCategory.REGULAR,
        branch_id: Optional[uuid.UUID] = None
    ) -> Optional[LockerRentStructure]:
        """Get active rent structure for given parameters"""
        today = date.today()
        
        query = self.db.query(LockerRentStructure).filter(
            and_(
                LockerRentStructure.tenant_id == self.tenant_id,
                LockerRentStructure.locker_size == locker_size.value,
                LockerRentStructure.customer_category == customer_category.value,
                LockerRentStructure.is_active == True,
                LockerRentStructure.effective_from <= today,
                LockerRentStructure.is_deleted == False
            )
        )
        
        # Check effective_to date
        query = query.filter(
            or_(
                LockerRentStructure.effective_to == None,
                LockerRentStructure.effective_to >= today
            )
        )
        
        # Branch-specific or general
        if branch_id:
            query = query.filter(
                or_(
                    LockerRentStructure.branch_id == branch_id,
                    LockerRentStructure.branch_id == None
                )
            ).order_by(LockerRentStructure.branch_id.desc())  # Prefer branch-specific
        else:
            query = query.filter(LockerRentStructure.branch_id == None)
        
        return query.first()
    
    async def list_rent_structures(
        self,
        locker_size: Optional[LockerSize] = None,
        customer_category: Optional[CustomerCategory] = None,
        branch_id: Optional[uuid.UUID] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[LockerRentStructure], int]:
        """List rent structures with filters"""
        query = self.db.query(LockerRentStructure).filter(
            and_(
                LockerRentStructure.tenant_id == self.tenant_id,
                LockerRentStructure.is_deleted == False
            )
        )
        
        if locker_size:
            query = query.filter(LockerRentStructure.locker_size == locker_size.value)
        
        if customer_category:
            query = query.filter(LockerRentStructure.customer_category == customer_category.value)
        
        if branch_id:
            query = query.filter(LockerRentStructure.branch_id == branch_id)
        
        if is_active is not None:
            query = query.filter(LockerRentStructure.is_active == is_active)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        structures = query.order_by(LockerRentStructure.created_at.desc()).offset(offset).limit(page_size).all()
        
        return structures, total
    
    async def update_rent_structure(
        self,
        structure_id: uuid.UUID,
        structure_data: LockerRentStructureUpdate
    ) -> Optional[LockerRentStructure]:
        """Update rent structure"""
        structure = await self.get_rent_structure(structure_id)
        if not structure:
            return None
        
        update_data = structure_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(structure, field, value)
        
        structure.updated_by = self.user_id
        structure.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(structure)
        
        return structure
    
    async def deactivate_rent_structure(
        self,
        structure_id: uuid.UUID
    ) -> Optional[LockerRentStructure]:
        """Deactivate a rent structure"""
        structure = await self.get_rent_structure(structure_id)
        if not structure:
            return None
        
        structure.is_active = False
        structure.effective_to = date.today()
        structure.updated_by = self.user_id
        structure.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(structure)
        
        return structure

    
    # ==================== RENT CALCULATION ====================
    
    async def calculate_rent(
        self,
        calculation_request: RentCalculationRequest
    ) -> RentCalculationResponse:
        """Calculate rent amount based on parameters"""
        # Get applicable rent structure
        structure = await self.get_active_rent_structure(
            locker_size=calculation_request.locker_size,
            customer_category=calculation_request.customer_category,
            branch_id=calculation_request.branch_id
        )
        
        if not structure:
            raise ValueError(
                f"No active rent structure found for size: {calculation_request.locker_size}, "
                f"category: {calculation_request.customer_category}"
            )
        
        # Calculate period in months
        period_months = self._calculate_months_between(
            calculation_request.period_from,
            calculation_request.period_to
        )
        
        # Get base rent based on frequency
        base_rent = self._get_base_rent_by_frequency(
            structure,
            calculation_request.rent_frequency,
            period_months
        )
        
        # Add location premium
        location_premium = Decimal("0")
        if structure.location_premium_percentage > 0:
            location_premium = (base_rent * structure.location_premium_percentage) / Decimal("100")
        elif structure.location_premium_amount > 0:
            location_premium = structure.location_premium_amount
        
        # Calculate subtotal before discount
        subtotal = base_rent + location_premium
        
        # Apply discount
        discount_amount = Decimal("0")
        if structure.discount_percentage > 0:
            discount_amount = (subtotal * structure.discount_percentage) / Decimal("100")
        elif structure.discount_amount > 0:
            discount_amount = structure.discount_amount
        
        # Apply advance payment discount
        if calculation_request.advance_payment and structure.advance_payment_discount > 0:
            advance_discount = (subtotal * structure.advance_payment_discount) / Decimal("100")
            discount_amount += advance_discount
        
        # Subtotal after discount
        subtotal_after_discount = subtotal - discount_amount
        
        # Calculate GST
        gst_amount = Decimal("0")
        if structure.gst_applicable and structure.gst_on_rent:
            gst_amount = (subtotal_after_discount * structure.gst_rate) / Decimal("100")
        
        # Total amount
        total_amount = subtotal_after_discount + gst_amount
        
        # Security deposit
        security_deposit = structure.security_deposit_amount
        
        # Add GST on deposit if applicable
        if structure.gst_applicable and structure.gst_on_deposit:
            deposit_gst = (security_deposit * structure.gst_rate) / Decimal("100")
            security_deposit += deposit_gst
        
        # Total payable (for new allocation)
        total_payable = total_amount + security_deposit
        
        return RentCalculationResponse(
            base_rent=base_rent,
            location_premium=location_premium,
            discount_amount=discount_amount,
            subtotal=subtotal_after_discount,
            gst_amount=gst_amount,
            total_amount=total_amount,
            security_deposit=security_deposit,
            total_payable=total_payable,
            rent_frequency=calculation_request.rent_frequency,
            period_months=period_months,
            gst_rate=structure.gst_rate,
            discount_percentage=structure.discount_percentage
        )
    
    def _calculate_months_between(self, start_date: date, end_date: date) -> int:
        """Calculate number of months between two dates"""
        delta = relativedelta(end_date, start_date)
        return delta.years * 12 + delta.months + (1 if delta.days > 0 else 0)
    
    def _get_base_rent_by_frequency(
        self,
        structure: LockerRentStructure,
        frequency: RentFrequency,
        period_months: int
    ) -> Decimal:
        """Get base rent based on payment frequency"""
        if frequency == RentFrequency.ANNUAL:
            return structure.base_rent_annual * Decimal(period_months / 12)
        elif frequency == RentFrequency.SEMI_ANNUAL:
            if structure.base_rent_semi_annual:
                return structure.base_rent_semi_annual * Decimal(period_months / 6)
            return (structure.base_rent_annual / Decimal("2")) * Decimal(period_months / 6)
        elif frequency == RentFrequency.QUARTERLY:
            if structure.base_rent_quarterly:
                return structure.base_rent_quarterly * Decimal(period_months / 3)
            return (structure.base_rent_annual / Decimal("4")) * Decimal(period_months / 3)
        elif frequency == RentFrequency.MONTHLY:
            if structure.base_rent_monthly:
                return structure.base_rent_monthly * Decimal(period_months)
            return (structure.base_rent_annual / Decimal("12")) * Decimal(period_months)
        
        return structure.base_rent_annual
    
    async def calculate_late_payment_penalty(
        self,
        allocation_id: uuid.UUID,
        overdue_amount: Decimal,
        due_date: date,
        payment_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Calculate late payment penalty"""
        allocation = self.db.query(LockerAllocation).filter(
            LockerAllocation.id == allocation_id
        ).first()
        
        if not allocation:
            raise ValueError(f"Allocation not found: {allocation_id}")
        
        # Get rent structure
        structure = await self.get_active_rent_structure(
            locker_size=LockerSize(allocation.locker.locker_size),
            customer_category=CustomerCategory.REGULAR,  # Get from customer if available
            branch_id=allocation.locker.branch_id
        )
        
        if not structure or not structure.late_payment_penalty_applicable:
            return {
                'penalty_applicable': False,
                'penalty_amount': Decimal("0"),
                'days_overdue': 0
            }
        
        # Calculate days overdue
        if not payment_date:
            payment_date = date.today()
        
        days_overdue = (payment_date - due_date).days
        
        # Check grace period
        if days_overdue <= structure.late_payment_grace_days:
            return {
                'penalty_applicable': False,
                'penalty_amount': Decimal("0"),
                'days_overdue': days_overdue,
                'within_grace_period': True
            }
        
        # Calculate penalty
        penalty_amount = Decimal("0")
        
        if structure.penalty_calculation_method == 'percentage':
            # Percentage-based penalty (per month or pro-rated)
            months_overdue = Decimal(days_overdue) / Decimal("30")
            penalty_amount = (overdue_amount * structure.late_payment_penalty_percentage / Decimal("100")) * months_overdue
        elif structure.penalty_calculation_method == 'flat_amount':
            # Flat amount penalty
            penalty_amount = structure.late_payment_penalty_flat_amount
        elif structure.penalty_calculation_method == 'both':
            # Both percentage and flat amount
            months_overdue = Decimal(days_overdue) / Decimal("30")
            percentage_penalty = (overdue_amount * structure.late_payment_penalty_percentage / Decimal("100")) * months_overdue
            penalty_amount = percentage_penalty + structure.late_payment_penalty_flat_amount
        
        return {
            'penalty_applicable': True,
            'penalty_amount': penalty_amount,
            'days_overdue': days_overdue,
            'overdue_months': float(Decimal(days_overdue) / Decimal("30")),
            'penalty_rate': float(structure.late_payment_penalty_percentage),
            'calculation_method': structure.penalty_calculation_method
        }
    
    async def get_other_charges(
        self,
        locker_size: LockerSize,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Decimal]:
        """Get other applicable charges"""
        structure = await self.get_active_rent_structure(
            locker_size=locker_size,
            customer_category=CustomerCategory.REGULAR,
            branch_id=branch_id
        )
        
        if not structure:
            return {
                'duplicate_key_charges': Decimal("500"),
                'locker_breaking_charges': Decimal("2000"),
                'transfer_charges': Decimal("500"),
                'closure_charges': Decimal("0")
            }
        
        return {
            'duplicate_key_charges': structure.duplicate_key_charges,
            'locker_breaking_charges': structure.locker_breaking_charges,
            'transfer_charges': structure.transfer_charges,
            'closure_charges': structure.closure_charges
        }
    
    # ==================== RENT WAIVERS & SPECIAL PRICING ====================
    
    async def check_rent_waiver_eligibility(
        self,
        customer_category: CustomerCategory,
        locker_size: LockerSize,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Check if customer is eligible for rent waiver"""
        structure = await self.get_active_rent_structure(
            locker_size=locker_size,
            customer_category=customer_category,
            branch_id=branch_id
        )
        
        if not structure or not structure.rent_waiver_applicable:
            return {
                'eligible': False,
                'waiver_conditions': None
            }
        
        return {
            'eligible': True,
            'waiver_conditions': structure.rent_waiver_conditions,
            'base_rent': structure.base_rent_annual
        }
    
    async def apply_promotional_discount(
        self,
        locker_size: LockerSize,
        customer_category: CustomerCategory,
        promotional_code: str,
        branch_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """Apply promotional discount (placeholder for future implementation)"""
        # This can be extended to support promotional codes
        return {
            'valid': False,
            'message': 'Promotional code feature not yet implemented'
        }
    
    # ==================== ANALYTICS & REPORTS ====================
    
    async def get_rent_structure_comparison(
        self,
        locker_size: LockerSize
    ) -> List[Dict[str, Any]]:
        """Compare rent structures across customer categories"""
        comparison = []
        
        for category in CustomerCategory:
            structure = await self.get_active_rent_structure(
                locker_size=locker_size,
                customer_category=category
            )
            
            if structure:
                comparison.append({
                    'customer_category': category.value,
                    'base_rent_annual': float(structure.base_rent_annual),
                    'security_deposit': float(structure.security_deposit_amount),
                    'gst_rate': float(structure.gst_rate),
                    'discount_percentage': float(structure.discount_percentage),
                    'late_penalty_rate': float(structure.late_payment_penalty_percentage)
                })
        
        return comparison
    
    async def get_pricing_summary(self) -> Dict[str, Any]:
        """Get pricing summary across all sizes and categories"""
        summary = {
            'by_size': {},
            'by_category': {},
            'total_structures': 0
        }
        
        structures = self.db.query(LockerRentStructure).filter(
            and_(
                LockerRentStructure.tenant_id == self.tenant_id,
                LockerRentStructure.is_active == True,
                LockerRentStructure.is_deleted == False
            )
        ).all()
        
        summary['total_structures'] = len(structures)
        
        for structure in structures:
            size = structure.locker_size
            category = structure.customer_category
            
            if size not in summary['by_size']:
                summary['by_size'][size] = {
                    'min_rent': float(structure.base_rent_annual),
                    'max_rent': float(structure.base_rent_annual),
                    'avg_rent': float(structure.base_rent_annual),
                    'count': 1
                }
            else:
                summary['by_size'][size]['min_rent'] = min(
                    summary['by_size'][size]['min_rent'],
                    float(structure.base_rent_annual)
                )
                summary['by_size'][size]['max_rent'] = max(
                    summary['by_size'][size]['max_rent'],
                    float(structure.base_rent_annual)
                )
                summary['by_size'][size]['count'] += 1
            
            if category not in summary['by_category']:
                summary['by_category'][category] = 1
            else:
                summary['by_category'][category] += 1
        
        return summary
