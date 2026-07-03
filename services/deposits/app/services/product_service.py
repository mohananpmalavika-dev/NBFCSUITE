"""
Product Service
Manages deposit products and interest slabs
"""

from decimal import Decimal
from datetime import date
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
import uuid


class ProductService:
    """
    Deposit Product Management Service
    CRUD operations for products and rate slabs
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_product(
        self,
        code: str,
        name: str,
        deposit_type: str,
        min_amount: Decimal,
        max_amount: Optional[Decimal],
        min_tenure_days: int,
        max_tenure_days: int,
        interest_method: str,
        default_interest_rate: Decimal,
        payout_frequency: str,
        created_by: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create new deposit product
        """
        from ..models import DepositProduct
        
        # Check if code already exists
        existing = self.db.query(DepositProduct).filter(
            DepositProduct.code == code
        ).first()
        
        if existing:
            raise ValueError(f"Product code already exists: {code}")
        
        product = DepositProduct(
            id=uuid.uuid4(),
            code=code,
            name=name,
            deposit_type=deposit_type,
            min_amount=min_amount,
            max_amount=max_amount,
            min_tenure_days=min_tenure_days,
            max_tenure_days=max_tenure_days,
            interest_method=interest_method,
            default_interest_rate=default_interest_rate,
            payout_frequency=payout_frequency,
            senior_citizen_rate_bonus=kwargs.get('senior_citizen_rate_bonus', Decimal('0.5')),
            premature_allowed=kwargs.get('premature_allowed', True),
            premature_penalty_percentage=kwargs.get('premature_penalty_percentage', Decimal('1.0')),
            auto_renewal_allowed=kwargs.get('auto_renewal_allowed', True),
            loan_against_deposit_allowed=kwargs.get('loan_against_deposit_allowed', True),
            tds_applicable=kwargs.get('tds_applicable', True),
            tds_rate=kwargs.get('tds_rate', Decimal('10.0')),
            status="ACTIVE",
            effective_from=kwargs.get('effective_from', date.today()),
            created_by=created_by
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return {
            "id": str(product.id),
            "code": product.code,
            "name": product.name,
            "deposit_type": product.deposit_type,
            "min_amount": float(product.min_amount),
            "max_amount": float(product.max_amount) if product.max_amount else None,
            "interest_rate": float(product.default_interest_rate),
            "status": product.status
        }
    
    def add_interest_slab(
        self,
        product_id: str,
        interest_rate: Decimal,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        min_tenure_days: Optional[int] = None,
        max_tenure_days: Optional[int] = None,
        senior_citizen_rate: Optional[Decimal] = None,
        effective_from: Optional[date] = None,
        effective_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Add interest rate slab to product
        """
        from ..models import InterestSlab, DepositProduct
        
        product = self.db.query(DepositProduct).filter(
            DepositProduct.id == product_id
        ).first()
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        slab = InterestSlab(
            id=uuid.uuid4(),
            product_id=product_id,
            min_amount=min_amount,
            max_amount=max_amount,
            min_tenure_days=min_tenure_days,
            max_tenure_days=max_tenure_days,
            interest_rate=interest_rate,
            senior_citizen_rate=senior_citizen_rate,
            effective_from=effective_from or date.today(),
            effective_to=effective_to
        )
        
        self.db.add(slab)
        self.db.commit()
        
        return {
            "slab_id": str(slab.id),
            "product_id": product_id,
            "interest_rate": float(interest_rate),
            "amount_range": {
                "min": float(min_amount) if min_amount else None,
                "max": float(max_amount) if max_amount else None
            },
            "tenure_range": {
                "min_days": min_tenure_days,
                "max_days": max_tenure_days
            }
        }
    
    def get_all_products(
        self,
        deposit_type: Optional[str] = None,
        status: str = "ACTIVE"
    ) -> List[Dict[str, Any]]:
        """
        Get all deposit products
        """
        from ..models import DepositProduct
        
        query = self.db.query(DepositProduct)
        
        if deposit_type:
            query = query.filter(DepositProduct.deposit_type == deposit_type)
        
        if status:
            query = query.filter(DepositProduct.status == status)
        
        products = query.order_by(DepositProduct.created_at.desc()).all()
        
        return [
            {
                "id": str(p.id),
                "code": p.code,
                "name": p.name,
                "deposit_type": p.deposit_type,
                "min_amount": float(p.min_amount),
                "max_amount": float(p.max_amount) if p.max_amount else None,
                "min_tenure_days": p.min_tenure_days,
                "max_tenure_days": p.max_tenure_days,
                "default_interest_rate": float(p.default_interest_rate) if p.default_interest_rate else None,
                "interest_method": p.interest_method,
                "payout_frequency": p.payout_frequency,
                "status": p.status
            }
            for p in products
        ]
    
    def get_product_details(
        self,
        product_id: str
    ) -> Dict[str, Any]:
        """
        Get product with all interest slabs
        """
        from ..models import DepositProduct
        
        product = self.db.query(DepositProduct).filter(
            DepositProduct.id == product_id
        ).first()
        
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        
        return {
            "id": str(product.id),
            "code": product.code,
            "name": product.name,
            "deposit_type": product.deposit_type,
            "min_amount": float(product.min_amount),
            "max_amount": float(product.max_amount) if product.max_amount else None,
            "min_tenure_days": product.min_tenure_days,
            "max_tenure_days": product.max_tenure_days,
            "interest_method": product.interest_method,
            "default_interest_rate": float(product.default_interest_rate) if product.default_interest_rate else None,
            "senior_citizen_rate_bonus": float(product.senior_citizen_rate_bonus),
            "payout_frequency": product.payout_frequency,
            "premature_allowed": product.premature_allowed,
            "premature_penalty_percentage": float(product.premature_penalty_percentage),
            "auto_renewal_allowed": product.auto_renewal_allowed,
            "loan_against_deposit_allowed": product.loan_against_deposit_allowed,
            "tds_applicable": product.tds_applicable,
            "tds_rate": float(product.tds_rate),
            "status": product.status,
            "interest_slabs": [
                {
                    "id": str(slab.id),
                    "min_amount": float(slab.min_amount) if slab.min_amount else None,
                    "max_amount": float(slab.max_amount) if slab.max_amount else None,
                    "min_tenure_days": slab.min_tenure_days,
                    "max_tenure_days": slab.max_tenure_days,
                    "interest_rate": float(slab.interest_rate),
                    "senior_citizen_rate": float(slab.senior_citizen_rate) if slab.senior_citizen_rate else None
                }
                for slab in product.interest_slabs
            ]
        }
    
    def seed_default_products(self):
        """
        Seed default FD/RD products for quick start
        """
        default_products = [
            {
                "code": "FD_REGULAR",
                "name": "Fixed Deposit - Regular",
                "deposit_type": "FIXED_DEPOSIT",
                "min_amount": Decimal('10000'),
                "max_amount": Decimal('10000000'),
                "min_tenure_days": 90,
                "max_tenure_days": 3650,
                "interest_method": "SIMPLE",
                "default_interest_rate": Decimal('7.0'),
                "payout_frequency": "ON_MATURITY"
            },
            {
                "code": "FD_SENIOR_CITIZEN",
                "name": "Fixed Deposit - Senior Citizen",
                "deposit_type": "FIXED_DEPOSIT",
                "min_amount": Decimal('10000'),
                "max_amount": Decimal('10000000'),
                "min_tenure_days": 180,
                "max_tenure_days": 3650,
                "interest_method": "SIMPLE",
                "default_interest_rate": Decimal('7.5'),
                "payout_frequency": "ON_MATURITY",
                "senior_citizen_rate_bonus": Decimal('0.5')
            },
            {
                "code": "FD_MONTHLY_INTEREST",
                "name": "Fixed Deposit - Monthly Interest",
                "deposit_type": "FIXED_DEPOSIT",
                "min_amount": Decimal('25000'),
                "max_amount": Decimal('10000000'),
                "min_tenure_days": 365,
                "max_tenure_days": 3650,
                "interest_method": "SIMPLE",
                "default_interest_rate": Decimal('6.75'),
                "payout_frequency": "MONTHLY"
            },
            {
                "code": "FD_CUMULATIVE",
                "name": "Fixed Deposit - Cumulative",
                "deposit_type": "FIXED_DEPOSIT",
                "min_amount": Decimal('10000'),
                "max_amount": Decimal('10000000'),
                "min_tenure_days": 365,
                "max_tenure_days": 3650,
                "interest_method": "COMPOUND_QUARTERLY",
                "default_interest_rate": Decimal('7.25'),
                "payout_frequency": "CUMULATIVE"
            },
            {
                "code": "RD_REGULAR",
                "name": "Recurring Deposit - Regular",
                "deposit_type": "RECURRING_DEPOSIT",
                "min_amount": Decimal('500'),
                "max_amount": Decimal('100000'),
                "min_tenure_days": 180,
                "max_tenure_days": 3650,
                "interest_method": "SIMPLE",
                "default_interest_rate": Decimal('7.0'),
                "payout_frequency": "ON_MATURITY"
            }
        ]
        
        created = []
        
        for product_data in default_products:
            try:
                result = self.create_product(**product_data)
                created.append(result)
            except ValueError:
                # Product already exists
                continue
        
        return {
            "message": f"Seeded {len(created)} products",
            "products": created
        }
