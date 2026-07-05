"""
Deposit Product Service

Handles all business logic for deposit products including:
- Product CRUD operations
- Interest calculations
- Maturity calculations
- Eligibility validation
- Product configuration
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from datetime import date, timedelta
from decimal import Decimal
import math

from backend.shared.database.deposit_models import DepositProduct
from backend.shared.common.response import CustomException


class DepositProductService:
    """Service for managing deposit products"""
    
    def __init__(self, db: Session, tenant_id: int, user_id: int):
        self.db = db
        self.tenant_id = tenant_id
        self.user_id = user_id
    
    # ==================== CRUD OPERATIONS ====================
    
    def create_product(self, product_data: Dict[str, Any]) -> DepositProduct:
        """
        Create new deposit product
        
        Args:
            product_data: Product configuration
            
        Returns:
            Created product
        """
        # Validate product type
        valid_types = ['savings', 'fd', 'rd', 'mis']
        if product_data.get('product_type') not in valid_types:
            raise CustomException(
                status_code=400,
                message=f"Invalid product type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Validate interest calculation method
        valid_methods = ['simple', 'compound']
        if product_data.get('interest_calculation_method') not in valid_methods:
            raise CustomException(
                status_code=400,
                message=f"Invalid calculation method. Must be one of: {', '.join(valid_methods)}"
            )
        
        # Check if product code already exists
        existing = self.db.query(DepositProduct).filter(
            and_(
                DepositProduct.tenant_id == self.tenant_id,
                DepositProduct.product_code == product_data.get('product_code'),
                DepositProduct.is_deleted == False
            )
        ).first()
        
        if existing:
            raise CustomException(
                status_code=400,
                message=f"Product code {product_data.get('product_code')} already exists"
            )
        
        # Validate product-specific requirements
        self._validate_product_config(product_data)
        
        # Create product
        product = DepositProduct(
            tenant_id=self.tenant_id,
            created_by=self.user_id,
            updated_by=self.user_id,
            **product_data
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def get_product(self, product_id: int) -> Optional[DepositProduct]:
        """Get product by ID"""
        product = self.db.query(DepositProduct).filter(
            and_(
                DepositProduct.id == product_id,
                DepositProduct.tenant_id == self.tenant_id,
                DepositProduct.is_deleted == False
            )
        ).first()
        
        if not product:
            raise CustomException(status_code=404, message="Product not found")
        
        return product
    
    def get_product_by_code(self, product_code: str) -> Optional[DepositProduct]:
        """Get product by code"""
        product = self.db.query(DepositProduct).filter(
            and_(
                DepositProduct.product_code == product_code,
                DepositProduct.tenant_id == self.tenant_id,
                DepositProduct.is_deleted == False
            )
        ).first()
        
        if not product:
            raise CustomException(status_code=404, message="Product not found")
        
        return product
    
    def list_products(
        self,
        product_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DepositProduct]:
        """List products with filters"""
        query = self.db.query(DepositProduct).filter(
            and_(
                DepositProduct.tenant_id == self.tenant_id,
                DepositProduct.is_deleted == False
            )
        )
        
        if product_type:
            query = query.filter(DepositProduct.product_type == product_type)
        
        if is_active is not None:
            query = query.filter(DepositProduct.is_active == is_active)
        
        products = query.offset(skip).limit(limit).all()
        return products
    
    def update_product(self, product_id: int, update_data: Dict[str, Any]) -> DepositProduct:
        """Update product"""
        product = self.get_product(product_id)
        
        # Validate if update includes product-specific config
        if 'product_type' in update_data and update_data['product_type'] != product.product_type:
            raise CustomException(
                status_code=400,
                message="Cannot change product type"
            )
        
        # Validate configuration
        merged_data = {**product.__dict__, **update_data}
        self._validate_product_config(merged_data)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        product.updated_by = self.user_id
        
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def delete_product(self, product_id: int) -> bool:
        """Soft delete product"""
        product = self.get_product(product_id)
        
        # Check if product has active accounts
        from backend.shared.database.deposit_models import DepositAccount
        active_accounts = self.db.query(DepositAccount).filter(
            and_(
                DepositAccount.deposit_product_id == product_id,
                DepositAccount.status == 'active',
                DepositAccount.is_deleted == False
            )
        ).count()
        
        if active_accounts > 0:
            raise CustomException(
                status_code=400,
                message=f"Cannot delete product with {active_accounts} active accounts"
            )
        
        product.is_deleted = True
        product.updated_by = self.user_id
        
        self.db.commit()
        return True
    
    # ==================== VALIDATION ====================
    
    def _validate_product_config(self, data: Dict[str, Any]) -> None:
        """Validate product configuration based on type"""
        product_type = data.get('product_type')
        
        if product_type == 'savings':
            self._validate_savings_config(data)
        elif product_type == 'fd':
            self._validate_fd_config(data)
        elif product_type == 'rd':
            self._validate_rd_config(data)
        elif product_type == 'mis':
            self._validate_mis_config(data)
    
    def _validate_savings_config(self, data: Dict[str, Any]) -> None:
        """Validate savings account configuration"""
        if not data.get('min_balance'):
            raise CustomException(
                status_code=400,
                message="Minimum balance is required for savings account"
            )
        
        if data.get('interest_payout_frequency') not in ['monthly', 'quarterly', 'on_demand']:
            raise CustomException(
                status_code=400,
                message="Invalid interest payout frequency for savings account"
            )
    
    def _validate_fd_config(self, data: Dict[str, Any]) -> None:
        """Validate fixed deposit configuration"""
        if not data.get('min_tenure_days'):
            raise CustomException(
                status_code=400,
                message="Minimum tenure is required for FD"
            )
        
        if not data.get('max_tenure_days'):
            raise CustomException(
                status_code=400,
                message="Maximum tenure is required for FD"
            )
        
        if data.get('min_tenure_days') < 7:
            raise CustomException(
                status_code=400,
                message="Minimum tenure for FD must be at least 7 days"
            )
    
    def _validate_rd_config(self, data: Dict[str, Any]) -> None:
        """Validate recurring deposit configuration"""
        if not data.get('min_tenure_days'):
            raise CustomException(
                status_code=400,
                message="Minimum tenure is required for RD"
            )
        
        if not data.get('installment_amount'):
            raise CustomException(
                status_code=400,
                message="Installment amount is required for RD"
            )
        
        if data.get('installment_frequency') not in ['monthly', 'quarterly']:
            raise CustomException(
                status_code=400,
                message="Invalid installment frequency for RD"
            )
    
    def _validate_mis_config(self, data: Dict[str, Any]) -> None:
        """Validate monthly income scheme configuration"""
        if not data.get('min_tenure_days'):
            raise CustomException(
                status_code=400,
                message="Minimum tenure is required for MIS"
            )
        
        if data.get('interest_payout_frequency') != 'monthly':
            raise CustomException(
                status_code=400,
                message="Interest payout must be monthly for MIS"
            )
    
    def validate_eligibility(
        self,
        product_id: int,
        amount: Decimal,
        tenure_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Validate if deposit amount and tenure are eligible for product
        
        Returns:
            Validation result with eligible flag and messages
        """
        product = self.get_product(product_id)
        
        errors = []
        
        # Check amount
        if amount < product.min_deposit_amount:
            errors.append(
                f"Minimum deposit amount is ₹{product.min_deposit_amount:,.2f}"
            )
        
        if product.max_deposit_amount and amount > product.max_deposit_amount:
            errors.append(
                f"Maximum deposit amount is ₹{product.max_deposit_amount:,.2f}"
            )
        
        # Check tenure (for FD/RD/MIS)
        if product.product_type in ['fd', 'rd', 'mis']:
            if not tenure_days:
                errors.append("Tenure is required for this product")
            else:
                if tenure_days < product.min_tenure_days:
                    errors.append(
                        f"Minimum tenure is {product.min_tenure_days} days"
                    )
                
                if product.max_tenure_days and tenure_days > product.max_tenure_days:
                    errors.append(
                        f"Maximum tenure is {product.max_tenure_days} days"
                    )
        
        return {
            "eligible": len(errors) == 0,
            "errors": errors,
            "product_code": product.product_code,
            "product_name": product.product_name
        }
    
    # ==================== CALCULATIONS ====================
    
    def calculate_simple_interest(
        self,
        principal: Decimal,
        rate: Decimal,
        days: int
    ) -> Dict[str, Decimal]:
        """
        Calculate simple interest
        
        Formula: Interest = Principal × Rate × Days / (100 × 365)
        """
        interest = (principal * rate * days) / (Decimal('100') * Decimal('365'))
        interest = interest.quantize(Decimal('0.01'))
        
        maturity_amount = principal + interest
        
        return {
            "principal": principal,
            "interest": interest,
            "maturity_amount": maturity_amount,
            "total_days": days,
            "rate": rate
        }
    
    def calculate_compound_interest(
        self,
        principal: Decimal,
        rate: Decimal,
        days: int,
        frequency: str = 'quarterly'
    ) -> Dict[str, Decimal]:
        """
        Calculate compound interest
        
        Formula: A = P × (1 + r/n)^(n×t)
        Where:
            A = Maturity Amount
            P = Principal
            r = Annual Rate (in decimal)
            n = Compounding frequency per year
            t = Time in years
        """
        # Convert frequency to number per year
        frequency_map = {
            'daily': 365,
            'monthly': 12,
            'quarterly': 4,
            'half_yearly': 2,
            'yearly': 1
        }
        
        n = frequency_map.get(frequency, 4)  # Default quarterly
        
        # Convert to decimal
        r = float(rate) / 100
        t = float(days) / 365
        
        # Calculate compound interest
        maturity_amount = float(principal) * math.pow((1 + r / n), (n * t))
        maturity_amount = Decimal(str(maturity_amount)).quantize(Decimal('0.01'))
        
        interest = maturity_amount - principal
        
        return {
            "principal": principal,
            "interest": interest,
            "maturity_amount": maturity_amount,
            "total_days": days,
            "rate": rate,
            "frequency": frequency
        }
    
    def calculate_fd_maturity(
        self,
        product_id: int,
        principal: Decimal,
        tenure_days: int,
        interest_rate: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Calculate FD maturity amount"""
        product = self.get_product(product_id)
        
        if product.product_type != 'fd':
            raise CustomException(
                status_code=400,
                message="This product is not a Fixed Deposit"
            )
        
        # Use product rate if not provided
        rate = interest_rate or product.interest_rate
        
        # Calculate based on method
        if product.interest_calculation_method == 'simple':
            result = self.calculate_simple_interest(principal, rate, tenure_days)
        else:
            freq = product.interest_calculation_frequency or 'quarterly'
            result = self.calculate_compound_interest(principal, rate, tenure_days, freq)
        
        # Add product details
        result['product_code'] = product.product_code
        result['product_name'] = product.product_name
        result['calculation_method'] = product.interest_calculation_method
        
        return result
    
    def calculate_rd_maturity(
        self,
        product_id: int,
        installment_amount: Decimal,
        total_installments: int,
        interest_rate: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Calculate RD maturity amount
        
        Formula for RD:
        M = P × n × (n + 1) / 2 × r / 1200
        
        Where:
            M = Maturity Interest
            P = Monthly Installment
            n = Number of Installments
            r = Rate of Interest per annum
        """
        product = self.get_product(product_id)
        
        if product.product_type != 'rd':
            raise CustomException(
                status_code=400,
                message="This product is not a Recurring Deposit"
            )
        
        # Use product rate if not provided
        rate = interest_rate or product.interest_rate
        
        # Calculate total principal
        total_principal = installment_amount * total_installments
        
        # Calculate interest using RD formula
        P = float(installment_amount)
        n = total_installments
        r = float(rate)
        
        interest = Decimal(str(P * n * (n + 1) / 2 * r / 1200))
        interest = interest.quantize(Decimal('0.01'))
        
        maturity_amount = total_principal + interest
        
        return {
            "installment_amount": installment_amount,
            "total_installments": total_installments,
            "total_principal": total_principal,
            "interest": interest,
            "maturity_amount": maturity_amount,
            "rate": rate,
            "product_code": product.product_code,
            "product_name": product.product_name
        }
    
    def calculate_mis_payout(
        self,
        product_id: int,
        principal: Decimal,
        tenure_days: int,
        interest_rate: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Calculate MIS monthly payout"""
        product = self.get_product(product_id)
        
        if product.product_type != 'mis':
            raise CustomException(
                status_code=400,
                message="This product is not a Monthly Income Scheme"
            )
        
        # Use product rate if not provided
        rate = interest_rate or product.interest_rate
        
        # Calculate monthly payout
        annual_interest = principal * rate / Decimal('100')
        monthly_payout = annual_interest / Decimal('12')
        monthly_payout = monthly_payout.quantize(Decimal('0.01'))
        
        # Calculate total payouts
        total_months = tenure_days // 30
        total_interest = monthly_payout * total_months
        
        return {
            "principal": principal,
            "rate": rate,
            "monthly_payout": monthly_payout,
            "total_months": total_months,
            "total_interest": total_interest,
            "maturity_amount": principal,  # Principal returned at maturity
            "product_code": product.product_code,
            "product_name": product.product_name
        }
    
    def calculate_premature_closure(
        self,
        product_id: int,
        principal: Decimal,
        days_held: int,
        interest_rate: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """Calculate premature closure amount with penalty"""
        product = self.get_product(product_id)
        
        if not product.premature_withdrawal_allowed:
            raise CustomException(
                status_code=400,
                message="Premature withdrawal not allowed for this product"
            )
        
        # Use product rate if not provided
        rate = interest_rate or product.interest_rate
        
        # Calculate interest at reduced rate
        penalty_percent = product.premature_withdrawal_penalty or Decimal('0')
        reduced_rate = rate - penalty_percent
        
        if reduced_rate < 0:
            reduced_rate = Decimal('0')
        
        # Calculate interest
        if product.interest_calculation_method == 'simple':
            interest_calc = self.calculate_simple_interest(
                principal, reduced_rate, days_held
            )
        else:
            freq = product.interest_calculation_frequency or 'quarterly'
            interest_calc = self.calculate_compound_interest(
                principal, reduced_rate, days_held, freq
            )
        
        # Calculate penalty amount
        penalty_amount = (principal * penalty_percent * days_held) / (Decimal('100') * Decimal('365'))
        penalty_amount = penalty_amount.quantize(Decimal('0.01'))
        
        closure_amount = interest_calc['maturity_amount'] - penalty_amount
        
        return {
            "principal": principal,
            "days_held": days_held,
            "original_rate": rate,
            "reduced_rate": reduced_rate,
            "penalty_percent": penalty_percent,
            "penalty_amount": penalty_amount,
            "interest_earned": interest_calc['interest'],
            "closure_amount": closure_amount,
            "product_code": product.product_code
        }
    
    # ==================== STATISTICS ====================
    
    def get_product_statistics(self, product_id: int) -> Dict[str, Any]:
        """Get statistics for a product"""
        from backend.shared.database.deposit_models import DepositAccount
        from sqlalchemy import func
        
        product = self.get_product(product_id)
        
        # Get account statistics
        stats = self.db.query(
            func.count(DepositAccount.id).label('total_accounts'),
            func.sum(DepositAccount.principal_amount).label('total_deposits'),
            func.sum(DepositAccount.current_balance).label('total_balance'),
            func.sum(DepositAccount.interest_earned).label('total_interest')
        ).filter(
            and_(
                DepositAccount.deposit_product_id == product_id,
                DepositAccount.is_deleted == False
            )
        ).first()
        
        # Get status breakdown
        status_counts = self.db.query(
            DepositAccount.status,
            func.count(DepositAccount.id)
        ).filter(
            and_(
                DepositAccount.deposit_product_id == product_id,
                DepositAccount.is_deleted == False
            )
        ).group_by(DepositAccount.status).all()
        
        return {
            "product": {
                "id": product.id,
                "code": product.product_code,
                "name": product.product_name,
                "type": product.product_type,
                "rate": float(product.interest_rate)
            },
            "statistics": {
                "total_accounts": stats.total_accounts or 0,
                "total_deposits": float(stats.total_deposits or 0),
                "total_balance": float(stats.total_balance or 0),
                "total_interest": float(stats.total_interest or 0)
            },
            "status_breakdown": {
                status: count for status, count in status_counts
            }
        }
