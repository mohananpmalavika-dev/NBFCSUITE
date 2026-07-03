"""
Rate Engine
Dynamic interest rate calculation based on slabs and conditions
"""

from decimal import Decimal
from datetime import date
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session


class RateEngine:
    """
    Intelligent Rate Calculator
    Determines applicable interest rate based on:
    - Amount slabs
    - Tenure slabs
    - Customer type (senior citizen)
    - Special conditions
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_applicable_rate(
        self,
        product_id: str,
        amount: Decimal,
        tenure_days: int,
        is_senior_citizen: bool = False,
        calculation_date: date = None
    ) -> Dict[str, Any]:
        """
        Calculate the applicable interest rate for a deposit
        Considers slabs, senior citizen bonus, and special rates
        """
        if calculation_date is None:
            calculation_date = date.today()
        
        from ..models import DepositProduct, InterestSlab
        
        # Fetch product
        product = self.db.query(DepositProduct).filter(
            DepositProduct.id == product_id
        ).first()
        
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Get applicable slab
        slab = self._find_applicable_slab(
            product_id, amount, tenure_days, calculation_date
        )
        
        if slab:
            base_rate = slab.interest_rate
            senior_rate = slab.senior_citizen_rate or (
                base_rate + product.senior_citizen_rate_bonus
            )
        else:
            base_rate = product.default_interest_rate or Decimal('0')
            senior_rate = base_rate + product.senior_citizen_rate_bonus
        
        applicable_rate = senior_rate if is_senior_citizen else base_rate
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "amount": float(amount),
            "tenure_days": tenure_days,
            "is_senior_citizen": is_senior_citizen,
            "base_rate": float(base_rate),
            "senior_citizen_bonus": float(product.senior_citizen_rate_bonus),
            "applicable_rate": float(applicable_rate),
            "slab_id": str(slab.id) if slab else None,
            "calculation_date": calculation_date.isoformat()
        }
    
    def _find_applicable_slab(
        self,
        product_id: str,
        amount: Decimal,
        tenure_days: int,
        calculation_date: date
    ) -> Optional[Any]:
        """
        Find the most specific applicable slab
        Priority: Amount + Tenure > Amount only > Tenure only
        """
        from ..models import InterestSlab
        
        query = self.db.query(InterestSlab).filter(
            InterestSlab.product_id == product_id
        )
        
        # Filter by effective dates
        query = query.filter(
            (InterestSlab.effective_from == None) | 
            (InterestSlab.effective_from <= calculation_date)
        ).filter(
            (InterestSlab.effective_to == None) |
            (InterestSlab.effective_to >= calculation_date)
        )
        
        slabs = query.all()
        
        if not slabs:
            return None
        
        # Find best matching slab
        best_match = None
        best_score = -1
        
        for slab in slabs:
            score = 0
            
            # Check amount match
            amount_match = True
            if slab.min_amount is not None and amount < slab.min_amount:
                amount_match = False
            if slab.max_amount is not None and amount > slab.max_amount:
                amount_match = False
            
            if not amount_match:
                continue
            
            # Check tenure match
            tenure_match = True
            if slab.min_tenure_days is not None and tenure_days < slab.min_tenure_days:
                tenure_match = False
            if slab.max_tenure_days is not None and tenure_days > slab.max_tenure_days:
                tenure_match = False
            
            if not tenure_match:
                continue
            
            # Calculate specificity score
            if slab.min_amount is not None or slab.max_amount is not None:
                score += 2
            if slab.min_tenure_days is not None or slab.max_tenure_days is not None:
                score += 2
            
            if score > best_score:
                best_score = score
                best_match = slab
        
        return best_match
    
    def get_rate_card(
        self,
        product_id: str,
        calculation_date: date = None
    ) -> List[Dict[str, Any]]:
        """
        Get complete rate card for a product
        Shows all applicable slabs
        """
        if calculation_date is None:
            calculation_date = date.today()
        
        from ..models import InterestSlab, DepositProduct
        
        product = self.db.query(DepositProduct).filter(
            DepositProduct.id == product_id
        ).first()
        
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        slabs = self.db.query(InterestSlab).filter(
            InterestSlab.product_id == product_id
        ).filter(
            (InterestSlab.effective_from == None) |
            (InterestSlab.effective_from <= calculation_date)
        ).filter(
            (InterestSlab.effective_to == None) |
            (InterestSlab.effective_to >= calculation_date)
        ).order_by(
            InterestSlab.min_amount,
            InterestSlab.min_tenure_days
        ).all()
        
        rate_card = []
        
        for slab in slabs:
            rate_card.append({
                "slab_id": str(slab.id),
                "amount_range": {
                    "min": float(slab.min_amount) if slab.min_amount else None,
                    "max": float(slab.max_amount) if slab.max_amount else None
                },
                "tenure_range": {
                    "min_days": slab.min_tenure_days,
                    "max_days": slab.max_tenure_days
                },
                "interest_rate": float(slab.interest_rate),
                "senior_citizen_rate": float(slab.senior_citizen_rate) if slab.senior_citizen_rate else None,
                "effective_from": slab.effective_from.isoformat() if slab.effective_from else None,
                "effective_to": slab.effective_to.isoformat() if slab.effective_to else None
            })
        
        return {
            "product_id": product_id,
            "product_name": product.name,
            "default_rate": float(product.default_interest_rate) if product.default_interest_rate else None,
            "senior_citizen_bonus": float(product.senior_citizen_rate_bonus),
            "slabs": rate_card
        }
    
    def compare_rates(
        self,
        amount: Decimal,
        tenure_days: int,
        is_senior_citizen: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Compare rates across all active products
        Helps customers choose best option
        """
        from ..models import DepositProduct
        
        products = self.db.query(DepositProduct).filter(
            DepositProduct.status == "ACTIVE"
        ).all()
        
        comparisons = []
        
        for product in products:
            try:
                rate_data = self.calculate_applicable_rate(
                    str(product.id),
                    amount,
                    tenure_days,
                    is_senior_citizen
                )
                
                comparisons.append({
                    "product_id": str(product.id),
                    "product_name": product.name,
                    "deposit_type": product.deposit_type,
                    "interest_rate": rate_data["applicable_rate"],
                    "interest_method": product.interest_method,
                    "payout_frequency": product.payout_frequency,
                    "premature_allowed": product.premature_allowed,
                    "auto_renewal_allowed": product.auto_renewal_allowed
                })
            except Exception:
                continue
        
        # Sort by interest rate descending
        comparisons.sort(key=lambda x: x["interest_rate"], reverse=True)
        
        return comparisons
