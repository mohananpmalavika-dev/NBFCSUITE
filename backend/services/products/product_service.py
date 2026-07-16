"""
Product Management Service

Business logic for product configuration and management
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid
import copy

from backend.services.products.product_models import (
    Product, ProductSummary, ProductClone, ProductFilter,
    ProductCalculation, ProductCalculationResult,
    ProductStatus, ProductCategory, InterestCalculationMethod,
    FeeChargeConfig, ChargeType
)


class ProductService:
    """Service for managing product configurations"""
    
    def __init__(self):
        self.products: Dict[str, Product] = {}
    
    # ==================== CRUD OPERATIONS ====================
    
    def create_product(self, product: Product, user_id: Optional[int] = None) -> Product:
        """Create new product"""
        # Generate ID if not provided
        if not product.product_id:
            product.product_id = f"prod_{uuid.uuid4().hex[:12]}"
        
        # Validate product code uniqueness
        if self._is_product_code_exists(product.product_code, exclude_id=product.product_id):
            raise ValueError(f"Product code '{product.product_code}' already exists")
        
        # Validate configurations
        self._validate_product(product)
        
        # Set timestamps
        product.created_at = datetime.utcnow()
        product.created_by = user_id
        
        # Store product
        self.products[product.product_id] = product
        
        return product
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        return self.products.get(product_id)
    
    def get_product_by_code(self, product_code: str) -> Optional[Product]:
        """Get product by code"""
        for product in self.products.values():
            if product.product_code == product_code:
                return product
        return None
    
    def update_product(
        self,
        product_id: str,
        updates: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> Product:
        """Update product"""
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Check if trying to change product code
        if 'product_code' in updates and updates['product_code'] != product.product_code:
            if self._is_product_code_exists(updates['product_code'], exclude_id=product_id):
                raise ValueError(f"Product code '{updates['product_code']}' already exists")
        
        # Update fields
        for key, value in updates.items():
            if hasattr(product, key):
                setattr(product, key, value)
        
        # Update timestamp
        product.updated_at = datetime.utcnow()
        product.updated_by = user_id
        
        # Validate updated product
        self._validate_product(product)
        
        return product
    
    def delete_product(self, product_id: str) -> bool:
        """Delete product (soft delete by setting status to discontinued)"""
        product = self.products.get(product_id)
        if not product:
            return False
        
        product.product_status = ProductStatus.DISCONTINUED
        product.updated_at = datetime.utcnow()
        
        return True
    
    def list_products(
        self,
        filters: Optional[ProductFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProductSummary]:
        """List products with optional filtering"""
        products = list(self.products.values())
        
        # Apply filters
        if filters:
            products = self._apply_filters(products, filters)
        
        # Sort by display order and creation date
        products.sort(key=lambda p: (p.display_order, p.created_at), reverse=True)
        
        # Pagination
        products = products[skip:skip + limit]
        
        # Convert to summaries
        summaries = [self._to_summary(p) for p in products]
        
        return summaries
    
    # ==================== PRODUCT OPERATIONS ====================
    
    def clone_product(
        self,
        source_product_id: str,
        new_product_code: str,
        new_product_name: str,
        modifications: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None
    ) -> Product:
        """Clone an existing product"""
        source_product = self.products.get(source_product_id)
        if not source_product:
            raise ValueError(f"Source product {source_product_id} not found")
        
        # Check if new code already exists
        if self._is_product_code_exists(new_product_code):
            raise ValueError(f"Product code '{new_product_code}' already exists")
        
        # Deep copy the product
        cloned_product = copy.deepcopy(source_product)
        
        # Update basic fields
        cloned_product.product_id = f"prod_{uuid.uuid4().hex[:12]}"
        cloned_product.product_code = new_product_code
        cloned_product.product_name = new_product_name
        cloned_product.product_status = ProductStatus.DRAFT
        cloned_product.created_at = datetime.utcnow()
        cloned_product.updated_at = None
        cloned_product.created_by = user_id
        cloned_product.updated_by = None
        cloned_product.version = "1.0"
        
        # Apply modifications if provided
        if modifications:
            for key, value in modifications.items():
                if hasattr(cloned_product, key):
                    setattr(cloned_product, key, value)
        
        # Store cloned product
        self.products[cloned_product.product_id] = cloned_product
        
        return cloned_product
    
    def activate_product(self, product_id: str, user_id: Optional[int] = None) -> Product:
        """Activate a product"""
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Validate product before activation
        self._validate_product(product)
        
        product.product_status = ProductStatus.ACTIVE
        product.updated_at = datetime.utcnow()
        product.updated_by = user_id
        
        return product
    
    def deactivate_product(self, product_id: str, user_id: Optional[int] = None) -> Product:
        """Deactivate a product"""
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        product.product_status = ProductStatus.INACTIVE
        product.updated_at = datetime.utcnow()
        product.updated_by = user_id
        
        return product
    
    # ==================== CALCULATIONS ====================
    
    def calculate_emi(
        self,
        product_id: str,
        principal_amount: float,
        tenure_months: int,
        interest_rate: Optional[float] = None
    ) -> ProductCalculationResult:
        """Calculate EMI and generate amortization schedule"""
        product = self.products.get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Use product's base rate if not provided
        if interest_rate is None:
            interest_rate = product.interest_config.base_rate
        
        # Validate amount and tenure
        if principal_amount < product.amount_config.min_amount:
            raise ValueError(f"Amount below minimum: {product.amount_config.min_amount}")
        if principal_amount > product.amount_config.max_amount:
            raise ValueError(f"Amount exceeds maximum: {product.amount_config.max_amount}")
        if tenure_months < product.tenure_config.min_tenure_months:
            raise ValueError(f"Tenure below minimum: {product.tenure_config.min_tenure_months}")
        if tenure_months > product.tenure_config.max_tenure_months:
            raise ValueError(f"Tenure exceeds maximum: {product.tenure_config.max_tenure_months}")
        
        # Calculate based on interest calculation method
        if product.interest_config.calculation_method == InterestCalculationMethod.REDUCING_BALANCE:
            emi_amount = self._calculate_reducing_balance_emi(
                principal_amount, interest_rate, tenure_months
            )
        elif product.interest_config.calculation_method == InterestCalculationMethod.FLAT_RATE:
            emi_amount = self._calculate_flat_rate_emi(
                principal_amount, interest_rate, tenure_months
            )
        else:
            emi_amount = self._calculate_reducing_balance_emi(
                principal_amount, interest_rate, tenure_months
            )
        
        # Apply rounding if configured
        if product.emi_config:
            emi_amount = self._apply_rounding(emi_amount, product.emi_config.rounding_to, product.emi_config.rounding_rule)
        
        # Calculate total interest and amount
        total_amount = emi_amount * tenure_months
        total_interest = total_amount - principal_amount
        
        # Calculate fees
        processing_fee = self._calculate_fee(product.fees_config.processing_fee, principal_amount)
        total_charges = processing_fee  # Add other charges as needed
        
        # Net disbursal amount
        net_disbursal_amount = principal_amount - total_charges
        
        # Generate EMI schedule
        emi_schedule = self._generate_emi_schedule(
            principal_amount, emi_amount, interest_rate, tenure_months
        )
        
        result = ProductCalculationResult(
            product_id=product_id,
            principal_amount=principal_amount,
            tenure_months=tenure_months,
            interest_rate=interest_rate,
            emi_amount=round(emi_amount, 2),
            total_interest=round(total_interest, 2),
            total_amount=round(total_amount, 2),
            processing_fee=round(processing_fee, 2),
            total_charges=round(total_charges, 2),
            net_disbursal_amount=round(net_disbursal_amount, 2),
            emi_schedule=emi_schedule
        )
        
        return result
    
    # ==================== HELPER METHODS ====================
    
    def _validate_product(self, product: Product) -> None:
        """Validate product configuration"""
        # Validate interest rates
        if product.interest_config.min_rate > product.interest_config.max_rate:
            raise ValueError("Minimum interest rate cannot be greater than maximum")
        
        if not (product.interest_config.min_rate <= product.interest_config.base_rate <= product.interest_config.max_rate):
            raise ValueError("Base rate must be between min and max rates")
        
        # Validate tenure
        if product.tenure_config.min_tenure_months > product.tenure_config.max_tenure_months:
            raise ValueError("Minimum tenure cannot be greater than maximum")
        
        # Validate amount
        if product.amount_config.min_amount > product.amount_config.max_amount:
            raise ValueError("Minimum amount cannot be greater than maximum")
        
        # Validate dates
        if product.expiry_date and product.expiry_date < product.effective_date:
            raise ValueError("Expiry date cannot be before effective date")
    
    def _is_product_code_exists(self, product_code: str, exclude_id: Optional[str] = None) -> bool:
        """Check if product code already exists"""
        for product in self.products.values():
            if product.product_code == product_code and product.product_id != exclude_id:
                return True
        return False
    
    def _apply_filters(self, products: List[Product], filters: ProductFilter) -> List[Product]:
        """Apply filters to product list"""
        filtered = products
        
        if filters.category:
            filtered = [p for p in filtered if p.product_category == filters.category]
        
        if filters.status:
            filtered = [p for p in filtered if p.product_status == filters.status]
        
        if filters.min_amount is not None:
            filtered = [p for p in filtered if p.amount_config.min_amount >= filters.min_amount]
        
        if filters.max_amount is not None:
            filtered = [p for p in filtered if p.amount_config.max_amount <= filters.max_amount]
        
        if filters.is_featured is not None:
            filtered = [p for p in filtered if p.is_featured == filters.is_featured]
        
        if filters.search_query:
            query = filters.search_query.lower()
            filtered = [
                p for p in filtered
                if query in p.product_name.lower() or
                   query in p.product_code.lower() or
                   (p.product_description and query in p.product_description.lower())
            ]
        
        if filters.tags:
            filtered = [
                p for p in filtered
                if any(tag in p.tags for tag in filters.tags)
            ]
        
        return filtered
    
    def _to_summary(self, product: Product) -> ProductSummary:
        """Convert product to summary"""
        return ProductSummary(
            product_id=product.product_id,
            product_code=product.product_code,
            product_name=product.product_name,
            product_category=product.product_category,
            product_status=product.product_status,
            base_rate=product.interest_config.base_rate,
            min_amount=product.amount_config.min_amount,
            max_amount=product.amount_config.max_amount,
            min_tenure_months=product.tenure_config.min_tenure_months,
            max_tenure_months=product.tenure_config.max_tenure_months,
            effective_date=product.effective_date,
            is_featured=product.is_featured,
            created_at=product.created_at
        )
    
    def _calculate_reducing_balance_emi(
        self,
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> float:
        """Calculate EMI using reducing balance method"""
        monthly_rate = annual_rate / (12 * 100)
        
        if monthly_rate == 0:
            return principal / tenure_months
        
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / (((1 + monthly_rate) ** tenure_months) - 1)
        
        return emi
    
    def _calculate_flat_rate_emi(
        self,
        principal: float,
        annual_rate: float,
        tenure_months: int
    ) -> float:
        """Calculate EMI using flat rate method"""
        total_interest = principal * (annual_rate / 100) * (tenure_months / 12)
        total_amount = principal + total_interest
        emi = total_amount / tenure_months
        
        return emi
    
    def _apply_rounding(self, amount: float, rounding_to: int, rule: str) -> float:
        """Apply rounding rules"""
        if rule == "round_up":
            return ((amount // rounding_to) + 1) * rounding_to
        elif rule == "round_down":
            return (amount // rounding_to) * rounding_to
        else:  # round_nearest
            return round(amount / rounding_to) * rounding_to
    
    def _calculate_fee(self, fee_config: Optional[FeeChargeConfig], base_amount: float) -> float:
        """Calculate fee based on configuration"""
        if not fee_config or not fee_config.is_active:
            return 0.0
        
        if fee_config.charge_type == ChargeType.FLAT and fee_config.flat_amount:
            fee = fee_config.flat_amount
        elif fee_config.charge_type == ChargeType.PERCENTAGE and fee_config.percentage:
            fee = base_amount * (fee_config.percentage / 100)
        else:
            fee = 0.0
        
        # Apply min/max limits
        if fee_config.min_amount and fee < fee_config.min_amount:
            fee = fee_config.min_amount
        if fee_config.max_amount and fee > fee_config.max_amount:
            fee = fee_config.max_amount
        
        # Add GST if applicable
        if fee_config.gst_applicable:
            fee = fee * (1 + fee_config.gst_percentage / 100)
        
        return fee
    
    def _generate_emi_schedule(
        self,
        principal: float,
        emi: float,
        annual_rate: float,
        tenure_months: int
    ) -> List[Dict[str, Any]]:
        """Generate EMI amortization schedule"""
        schedule = []
        balance = principal
        monthly_rate = annual_rate / (12 * 100)
        
        for month in range(1, tenure_months + 1):
            interest = balance * monthly_rate
            principal_component = emi - interest
            balance = balance - principal_component
            
            # Adjust last EMI for rounding differences
            if month == tenure_months:
                principal_component += balance
                balance = 0
            
            schedule.append({
                "installment_no": month,
                "emi_amount": round(emi, 2),
                "principal_component": round(principal_component, 2),
                "interest_component": round(interest, 2),
                "outstanding_balance": round(max(balance, 0), 2)
            })
        
        return schedule


# Global instance
product_service = ProductService()
