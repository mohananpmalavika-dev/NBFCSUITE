"""
Offer Service

Service for managing pre-approved offers, calculating eligibility,
and tracking offer usage.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

from backend.shared.database.decision_models import PreApprovedOffer, DecisionLimit
from backend.services.decision.schemas import (
    PreApprovedOfferCreate,
    PreApprovedOfferResponse,
    OfferCalculateRequest,
    OfferType,
    OfferStatus
)


class OfferService:
    """Service for managing pre-approved offers"""

    def __init__(self, db: AsyncSession, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id

    async def calculate_offer(
        self,
        request: OfferCalculateRequest
    ) -> Dict[str, Any]:
        """
        Calculate pre-approved offer for a customer.
        
        This analyzes customer data, credit history, and applies
        business rules to determine offer terms.
        """
        # TODO: Fetch customer data
        # customer = await customer_service.get_customer(request.customer_id)
        
        # TODO: Fetch loan history
        # loan_history = await loan_service.get_customer_loans(request.customer_id)
        
        # TODO: Calculate credit score or fetch from bureau
        credit_score = 750  # Placeholder
        
        # Calculate approved amount based on rules
        approved_amount = await self._calculate_approved_amount(
            request.customer_id,
            request.product_id,
            credit_score
        )
        
        # Calculate interest rate
        interest_rate = await self._calculate_interest_rate(
            credit_score,
            request.product_id
        )
        
        # Determine tenure range
        min_tenure, max_tenure = await self._calculate_tenure_range(
            approved_amount,
            request.product_id
        )
        
        # Calculate processing fee
        processing_fee = await self._calculate_processing_fee(
            approved_amount,
            request.product_id
        )
        
        # Check for fee waiver eligibility
        processing_fee_waiver = await self._check_fee_waiver_eligibility(
            request.customer_id,
            credit_score
        )
        
        return {
            "customer_id": request.customer_id,
            "product_id": request.product_id,
            "offer_type": request.offer_type,
            "approved_amount": approved_amount,
            "min_amount": approved_amount * Decimal("0.2"),  # 20% of approved
            "max_amount": approved_amount,
            "interest_rate": interest_rate,
            "special_rate": credit_score >= 780,
            "min_tenure": min_tenure,
            "max_tenure": max_tenure,
            "processing_fee": processing_fee if not processing_fee_waiver else Decimal("0"),
            "processing_fee_waiver": processing_fee_waiver,
            "credit_score": credit_score,
            "validity_days": request.validity_days
        }

    async def create_offer(
        self,
        data: PreApprovedOfferCreate
    ) -> PreApprovedOffer:
        """Create a new pre-approved offer"""
        # Generate offer code
        offer_code = await self._generate_offer_code()
        
        # Validate amounts
        if data.max_amount < data.min_amount:
            raise ValueError("Maximum amount must be greater than minimum amount")
        
        if data.approved_amount > data.max_amount:
            raise ValueError("Approved amount cannot exceed maximum amount")
        
        # Create offer
        offer = PreApprovedOffer(
            offer_code=offer_code,
            customer_id=data.customer_id,
            product_id=data.product_id,
            offer_type=data.offer_type.value,
            approved_amount=data.approved_amount,
            min_amount=data.min_amount,
            max_amount=data.max_amount,
            interest_rate=data.interest_rate,
            special_rate=data.special_rate,
            min_tenure=data.min_tenure,
            max_tenure=data.max_tenure,
            processing_fee=data.processing_fee,
            processing_fee_waiver=data.processing_fee_waiver,
            benefits=data.benefits,
            valid_from=data.valid_from,
            valid_until=data.valid_until,
            calculation_factors=data.calculation_factors,
            source="system",
            status=OfferStatus.ACTIVE.value,
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id
        )
        
        self.db.add(offer)
        await self.db.commit()
        await self.db.refresh(offer)
        
        return offer

    async def get_offer(self, offer_id: int) -> Optional[PreApprovedOffer]:
        """Get offer by ID"""
        query = select(PreApprovedOffer).where(
            and_(
                PreApprovedOffer.id == offer_id,
                PreApprovedOffer.tenant_id == self.tenant_id,
                PreApprovedOffer.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_offer_by_code(self, offer_code: str) -> Optional[PreApprovedOffer]:
        """Get offer by code"""
        query = select(PreApprovedOffer).where(
            and_(
                PreApprovedOffer.offer_code == offer_code,
                PreApprovedOffer.tenant_id == self.tenant_id,
                PreApprovedOffer.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_customer_offers(
        self,
        customer_id: int,
        active_only: bool = True
    ) -> List[PreApprovedOffer]:
        """Get all offers for a customer"""
        conditions = [
            PreApprovedOffer.customer_id == customer_id,
            PreApprovedOffer.tenant_id == self.tenant_id,
            PreApprovedOffer.is_deleted == False
        ]
        
        if active_only:
            now = datetime.utcnow()
            conditions.extend([
                PreApprovedOffer.status == OfferStatus.ACTIVE.value,
                PreApprovedOffer.valid_from <= now,
                PreApprovedOffer.valid_until >= now
            ])
        
        query = select(PreApprovedOffer).where(
            and_(*conditions)
        ).order_by(
            PreApprovedOffer.created_at.desc()
        )
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_offers(
        self,
        offer_type: Optional[str] = None,
        status: Optional[str] = None,
        customer_id: Optional[int] = None,
        product_id: Optional[int] = None,
        valid_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[PreApprovedOffer], int]:
        """List offers with filters"""
        conditions = [
            PreApprovedOffer.tenant_id == self.tenant_id,
            PreApprovedOffer.is_deleted == False
        ]
        
        if offer_type:
            conditions.append(PreApprovedOffer.offer_type == offer_type)
        
        if status:
            conditions.append(PreApprovedOffer.status == status)
        
        if customer_id:
            conditions.append(PreApprovedOffer.customer_id == customer_id)
        
        if product_id:
            conditions.append(PreApprovedOffer.product_id == product_id)
        
        if valid_only:
            now = datetime.utcnow()
            conditions.extend([
                PreApprovedOffer.valid_from <= now,
                PreApprovedOffer.valid_until >= now
            ])
        
        # Count query
        count_query = select(func.count(PreApprovedOffer.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Data query
        query = select(PreApprovedOffer).where(
            and_(*conditions)
        ).order_by(
            PreApprovedOffer.created_at.desc()
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        offers = list(result.scalars().all())
        
        return offers, total

    async def use_offer(
        self,
        offer_id: int,
        application_id: int
    ) -> PreApprovedOffer:
        """Mark offer as used"""
        offer = await self.get_offer(offer_id)
        
        if not offer:
            raise ValueError("Offer not found")
        
        if offer.status != OfferStatus.ACTIVE.value:
            raise ValueError(f"Offer is {offer.status}, cannot use")
        
        # Check validity
        now = datetime.utcnow()
        if now < offer.valid_from or now > offer.valid_until:
            raise ValueError("Offer is not currently valid")
        
        offer.status = OfferStatus.USED.value
        offer.used_at = now
        offer.used_by = self.user_id
        offer.application_id = application_id
        offer.updated_by = self.user_id
        offer.updated_at = now
        
        await self.db.commit()
        await self.db.refresh(offer)
        
        return offer

    async def increment_view_count(self, offer_id: int):
        """Increment offer view count"""
        offer = await self.get_offer(offer_id)
        
        if offer:
            offer.viewed_count += 1
            offer.last_viewed_at = datetime.utcnow()
            await self.db.commit()

    async def cancel_offer(self, offer_id: int, reason: str) -> PreApprovedOffer:
        """Cancel an offer"""
        offer = await self.get_offer(offer_id)
        
        if not offer:
            raise ValueError("Offer not found")
        
        offer.status = OfferStatus.CANCELLED.value
        offer.updated_by = self.user_id
        offer.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(offer)
        
        return offer

    async def expire_offers(self) -> int:
        """Mark expired offers as expired"""
        now = datetime.utcnow()
        
        # Find active offers past valid_until
        query = select(PreApprovedOffer).where(
            and_(
                PreApprovedOffer.status == OfferStatus.ACTIVE.value,
                PreApprovedOffer.valid_until < now,
                PreApprovedOffer.tenant_id == self.tenant_id,
                PreApprovedOffer.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        expired_offers = list(result.scalars().all())
        
        for offer in expired_offers:
            offer.status = OfferStatus.EXPIRED.value
            offer.updated_by = self.user_id
            offer.updated_at = now
        
        await self.db.commit()
        
        return len(expired_offers)

    async def get_offer_statistics(self) -> Dict[str, Any]:
        """Get offer statistics"""
        now = datetime.utcnow()
        
        # Total active offers
        active_query = select(func.count(PreApprovedOffer.id)).where(
            and_(
                PreApprovedOffer.status == OfferStatus.ACTIVE.value,
                PreApprovedOffer.valid_from <= now,
                PreApprovedOffer.valid_until >= now,
                PreApprovedOffer.tenant_id == self.tenant_id,
                PreApprovedOffer.is_deleted == False
            )
        )
        active_result = await self.db.execute(active_query)
        total_active = active_result.scalar() or 0
        
        # Total used offers
        used_query = select(func.count(PreApprovedOffer.id)).where(
            and_(
                PreApprovedOffer.status == OfferStatus.USED.value,
                PreApprovedOffer.tenant_id == self.tenant_id,
                PreApprovedOffer.is_deleted == False
            )
        )
        used_result = await self.db.execute(used_query)
        total_used = used_result.scalar() or 0
        
        # Total expired offers
        expired_query = select(func.count(PreApprovedOffer.id)).where(
            and_(
                PreApprovedOffer.status == OfferStatus.EXPIRED.value,
                PreApprovedOffer.tenant_id == self.tenant_id,
                PreApprovedOffer.is_deleted == False
            )
        )
        expired_result = await self.db.execute(expired_query)
        total_expired = expired_result.scalar() or 0
        
        # Calculate conversion rate
        total_offers = total_active + total_used + total_expired
        conversion_rate = (total_used / total_offers * 100) if total_offers > 0 else 0
        
        return {
            "total_active": total_active,
            "total_used": total_used,
            "total_expired": total_expired,
            "total_offers": total_offers,
            "conversion_rate": round(conversion_rate, 2)
        }

    # Helper methods

    async def _generate_offer_code(self) -> str:
        """Generate unique offer code"""
        now = datetime.utcnow()
        prefix = f"OFF-{now.strftime('%Y%m')}"
        
        # Get count for this month
        query = select(func.count(PreApprovedOffer.id)).where(
            and_(
                PreApprovedOffer.offer_code.like(f"{prefix}%"),
                PreApprovedOffer.tenant_id == self.tenant_id
            )
        )
        result = await self.db.execute(query)
        count = result.scalar() or 0
        
        return f"{prefix}-{count + 1:05d}"

    async def _calculate_approved_amount(
        self,
        customer_id: int,
        product_id: int,
        credit_score: int
    ) -> Decimal:
        """Calculate approved loan amount based on customer profile"""
        # Base amount by credit score
        if credit_score >= 780:
            base_amount = Decimal("1000000")  # 10 lakhs
        elif credit_score >= 750:
            base_amount = Decimal("750000")  # 7.5 lakhs
        elif credit_score >= 700:
            base_amount = Decimal("500000")  # 5 lakhs
        elif credit_score >= 650:
            base_amount = Decimal("300000")  # 3 lakhs
        else:
            base_amount = Decimal("100000")  # 1 lakh
        
        # TODO: Adjust based on income, existing loans, etc.
        
        return base_amount

    async def _calculate_interest_rate(
        self,
        credit_score: int,
        product_id: int
    ) -> Decimal:
        """Calculate interest rate based on credit score"""
        # Base rate
        base_rate = Decimal("14.0")
        
        # Adjust by credit score
        if credit_score >= 780:
            rate = base_rate - Decimal("2.5")  # 11.5%
        elif credit_score >= 750:
            rate = base_rate - Decimal("2.0")  # 12.0%
        elif credit_score >= 720:
            rate = base_rate - Decimal("1.5")  # 12.5%
        elif credit_score >= 700:
            rate = base_rate - Decimal("1.0")  # 13.0%
        elif credit_score >= 680:
            rate = base_rate - Decimal("0.5")  # 13.5%
        else:
            rate = base_rate  # 14.0%
        
        return rate

    async def _calculate_tenure_range(
        self,
        amount: Decimal,
        product_id: int
    ) -> tuple[int, int]:
        """Calculate tenure range"""
        # Standard tenure range
        if amount <= 100000:
            return 6, 36  # 6 months to 3 years
        elif amount <= 500000:
            return 12, 60  # 1 to 5 years
        else:
            return 12, 84  # 1 to 7 years

    async def _calculate_processing_fee(
        self,
        amount: Decimal,
        product_id: int
    ) -> Decimal:
        """Calculate processing fee"""
        # 1% of loan amount
        fee = amount * Decimal("0.01")
        
        # Min and max
        min_fee = Decimal("500")
        max_fee = Decimal("10000")
        
        return max(min_fee, min(fee, max_fee))

    async def _check_fee_waiver_eligibility(
        self,
        customer_id: int,
        credit_score: int
    ) -> bool:
        """Check if customer is eligible for fee waiver"""
        # High credit score gets fee waiver
        if credit_score >= 780:
            return True
        
        # TODO: Check if existing customer with good repayment history
        
        return False

