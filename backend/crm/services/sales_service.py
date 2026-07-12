"""
CRM Sales Automation Service
Business logic for products, quotes, and orders
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

from backend.shared.database.crm_sales_models import (
    Product, Quote, QuoteItem, Order, OrderItem
)
from backend.shared.schemas.crm_sales_schemas import (
    ProductCreate, ProductUpdate,
    QuoteCreate, QuoteUpdate, QuoteItemCreate,
    OrderCreate, OrderUpdate, OrderItemCreate
)


def model_to_dict(obj):
    """Convert SQLAlchemy model to dictionary with proper serialization"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        if isinstance(value, UUID):
            result[column.name] = str(value)
        elif isinstance(value, (datetime, date)):
            result[column.name] = value.isoformat()
        elif isinstance(value, Decimal):
            result[column.name] = float(value)
        elif hasattr(value, 'value'):  # Enum
            result[column.name] = value.value
        else:
            result[column.name] = value
    return result


# ============================================================================
# PRODUCT SERVICE
# ============================================================================

class ProductService:
    """Service for Product Catalog operations"""
    
    @staticmethod
    def generate_product_code(db: Session, tenant_id: str) -> str:
        """Generate unique product code"""
        count = db.query(func.count(Product.id)).filter(
            Product.tenant_id == tenant_id,
            Product.is_deleted == False
        ).scalar()
        
        product_code = f"PROD-{str(count + 1).zfill(6)}"
        
        while db.query(Product).filter(
            Product.tenant_id == tenant_id,
            Product.product_code == product_code
        ).first():
            count += 1
            product_code = f"PROD-{str(count + 1).zfill(6)}"
        
        return product_code
    
    @staticmethod
    def create_product(
        db: Session,
        product_data: ProductCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new product"""
        try:
            # Check for duplicate product code
            existing = db.query(Product).filter(
                Product.tenant_id == tenant_id,
                Product.product_code == product_data.product_code,
                Product.is_deleted == False
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_PRODUCT_CODE",
                        "message": f"Product code {product_data.product_code} already exists"
                    }
                }
            
            product = Product(
                tenant_id=tenant_id,
                **product_data.dict(exclude_unset=True),
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(product)
            db.commit()
            db.refresh(product)
            
            return {
                "success": True,
                "message": "Product created successfully",
                "data": model_to_dict(product)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "PRODUCT_CREATE_FAILED",
                    "message": f"Failed to create product: {str(e)}"
                }
            }
    
    @staticmethod
    def get_product(
        db: Session,
        product_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get product by ID"""
        try:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.tenant_id == tenant_id,
                Product.is_deleted == False
            ).first()
            
            if not product:
                return {
                    "success": False,
                    "error": {
                        "code": "PRODUCT_NOT_FOUND",
                        "message": "Product not found"
                    }
                }
            
            return {
                "success": True,
                "data": model_to_dict(product)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "PRODUCT_GET_FAILED",
                    "message": f"Failed to get product: {str(e)}"
                }
            }
    
    @staticmethod
    def list_products(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List products with filters and pagination"""
        try:
            query = db.query(Product).filter(
                Product.tenant_id == tenant_id,
                Product.is_deleted == False
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Product.product_name.ilike(search_filter),
                        Product.product_code.ilike(search_filter),
                        Product.sku.ilike(search_filter),
                        Product.barcode.ilike(search_filter)
                    )
                )
            
            if category:
                query = query.filter(Product.product_category == category)
            
            if status:
                query = query.filter(Product.status == status)
            
            total = query.count()
            products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
            
            return {
                "success": True,
                "data": {
                    "products": [model_to_dict(p) for p in products],
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "total_pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "PRODUCT_LIST_FAILED",
                    "message": f"Failed to list products: {str(e)}"
                }
            }
    
    @staticmethod
    def update_product(
        db: Session,
        product_id: UUID,
        product_data: ProductUpdate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update product"""
        try:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.tenant_id == tenant_id,
                Product.is_deleted == False
            ).first()
            
            if not product:
                return {
                    "success": False,
                    "error": {
                        "code": "PRODUCT_NOT_FOUND",
                        "message": "Product not found"
                    }
                }
            
            update_data = product_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(product, field, value)
            
            product.updated_by = user_id
            product.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(product)
            
            return {
                "success": True,
                "message": "Product updated successfully",
                "data": model_to_dict(product)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "PRODUCT_UPDATE_FAILED",
                    "message": f"Failed to update product: {str(e)}"
                }
            }
    
    @staticmethod
    def delete_product(
        db: Session,
        product_id: UUID,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Soft delete product"""
        try:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.tenant_id == tenant_id,
                Product.is_deleted == False
            ).first()
            
            if not product:
                return {
                    "success": False,
                    "error": {
                        "code": "PRODUCT_NOT_FOUND",
                        "message": "Product not found"
                    }
                }
            
            product.is_deleted = True
            product.deleted_at = datetime.utcnow()
            product.deleted_by = user_id
            
            db.commit()
            
            return {
                "success": True,
                "message": "Product deleted successfully"
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "PRODUCT_DELETE_FAILED",
                    "message": f"Failed to delete product: {str(e)}"
                }
            }


# ============================================================================
# QUOTE SERVICE
# ============================================================================

class QuoteService:
    """Service for Quote Management operations"""
    
    @staticmethod
    def generate_quote_number(db: Session, tenant_id: str) -> str:
        """Generate unique quote number"""
        count = db.query(func.count(Quote.id)).filter(
            Quote.tenant_id == tenant_id,
            Quote.is_deleted == False
        ).scalar()
        
        today = datetime.now().strftime("%Y%m%d")
        quote_number = f"QT-{today}-{str(count + 1).zfill(4)}"
        
        while db.query(Quote).filter(
            Quote.tenant_id == tenant_id,
            Quote.quote_number == quote_number
        ).first():
            count += 1
            quote_number = f"QT-{today}-{str(count + 1).zfill(4)}"
        
        return quote_number
    
    @staticmethod
    def create_quote(
        db: Session,
        quote_data: QuoteCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new quote with line items"""
        try:
            quote_number = QuoteService.generate_quote_number(db, tenant_id)
            
            # Extract items
            items_data = quote_data.items
            quote_dict = quote_data.dict(exclude={'items'})
            
            # Create quote
            quote = Quote(
                tenant_id=tenant_id,
                quote_number=quote_number,
                status="draft",
                **quote_dict,
                quote_owner_id=user_id,
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(quote)
            db.flush()  # Get quote ID
            
            # Create quote items
            for item_data in items_data:
                item = QuoteItem(
                    quote_id=quote.id,
                    **item_data.dict()
                )
                db.add(item)
            
            db.commit()
            db.refresh(quote)
            
            # Load items
            quote_items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote.id).all()
            
            result = model_to_dict(quote)
            result['items'] = [model_to_dict(item) for item in quote_items]
            
            return {
                "success": True,
                "message": "Quote created successfully",
                "data": result
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "QUOTE_CREATE_FAILED",
                    "message": f"Failed to create quote: {str(e)}"
                }
            }
    
    @staticmethod
    def get_quote(
        db: Session,
        quote_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get quote by ID with items"""
        try:
            quote = db.query(Quote).filter(
                Quote.id == quote_id,
                Quote.tenant_id == tenant_id,
                Quote.is_deleted == False
            ).first()
            
            if not quote:
                return {
                    "success": False,
                    "error": {
                        "code": "QUOTE_NOT_FOUND",
                        "message": "Quote not found"
                    }
                }
            
            # Load items
            items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).all()
            
            result = model_to_dict(quote)
            result['items'] = [model_to_dict(item) for item in items]
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "QUOTE_GET_FAILED",
                    "message": f"Failed to get quote: {str(e)}"
                }
            }
    
    @staticmethod
    def list_quotes(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        status: Optional[str] = None,
        account_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """List quotes with filters and pagination"""
        try:
            query = db.query(Quote).filter(
                Quote.tenant_id == tenant_id,
                Quote.is_deleted == False
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(
                    or_(
                        Quote.quote_number.ilike(search_filter),
                        Quote.quote_title.ilike(search_filter)
                    )
                )
            
            if status:
                query = query.filter(Quote.status == status)
            
            if account_id:
                query = query.filter(Quote.account_id == account_id)
            
            total = query.count()
            quotes = query.order_by(Quote.created_at.desc()).offset(skip).limit(limit).all()
            
            # Load items for each quote
            results = []
            for quote in quotes:
                quote_dict = model_to_dict(quote)
                items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote.id).all()
                quote_dict['items'] = [model_to_dict(item) for item in items]
                results.append(quote_dict)
            
            return {
                "success": True,
                "data": {
                    "quotes": results,
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "total_pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "QUOTE_LIST_FAILED",
                    "message": f"Failed to list quotes: {str(e)}"
                }
            }
    
    @staticmethod
    def update_quote(
        db: Session,
        quote_id: UUID,
        quote_data: QuoteUpdate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update quote"""
        try:
            quote = db.query(Quote).filter(
                Quote.id == quote_id,
                Quote.tenant_id == tenant_id,
                Quote.is_deleted == False
            ).first()
            
            if not quote:
                return {
                    "success": False,
                    "error": {
                        "code": "QUOTE_NOT_FOUND",
                        "message": "Quote not found"
                    }
                }
            
            update_data = quote_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(quote, field, value)
            
            quote.updated_by = user_id
            quote.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(quote)
            
            # Load items
            items = db.query(QuoteItem).filter(QuoteItem.quote_id == quote_id).all()
            
            result = model_to_dict(quote)
            result['items'] = [model_to_dict(item) for item in items]
            
            return {
                "success": True,
                "message": "Quote updated successfully",
                "data": result
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "QUOTE_UPDATE_FAILED",
                    "message": f"Failed to update quote: {str(e)}"
                }
            }
    
    @staticmethod
    def update_quote_status(
        db: Session,
        quote_id: UUID,
        new_status: str,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update quote status"""
        try:
            quote = db.query(Quote).filter(
                Quote.id == quote_id,
                Quote.tenant_id == tenant_id,
                Quote.is_deleted == False
            ).first()
            
            if not quote:
                return {
                    "success": False,
                    "error": {
                        "code": "QUOTE_NOT_FOUND",
                        "message": "Quote not found"
                    }
                }
            
            quote.status = new_status
            
            if new_status == "accepted":
                quote.accepted_date = date.today()
            elif new_status == "rejected":
                quote.rejected_date = date.today()
            
            quote.updated_by = user_id
            quote.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(quote)
            
            return {
                "success": True,
                "message": f"Quote status updated to {new_status}",
                "data": model_to_dict(quote)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "QUOTE_STATUS_UPDATE_FAILED",
                    "message": f"Failed to update quote status: {str(e)}"
                }
            }


# ============================================================================
# ORDER SERVICE
# ============================================================================

class OrderService:
    """Service for Order Management operations"""
    
    @staticmethod
    def generate_order_number(db: Session, tenant_id: str) -> str:
        """Generate unique order number"""
        count = db.query(func.count(Order.id)).filter(
            Order.tenant_id == tenant_id,
            Order.is_deleted == False
        ).scalar()
        
        today = datetime.now().strftime("%Y%m%d")
        order_number = f"ORD-{today}-{str(count + 1).zfill(4)}"
        
        while db.query(Order).filter(
            Order.tenant_id == tenant_id,
            Order.order_number == order_number
        ).first():
            count += 1
            order_number = f"ORD-{today}-{str(count + 1).zfill(4)}"
        
        return order_number
    
    @staticmethod
    def create_order(
        db: Session,
        order_data: OrderCreate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Create a new order with line items"""
        try:
            order_number = OrderService.generate_order_number(db, tenant_id)
            
            # Extract items
            items_data = order_data.items
            order_dict = order_data.dict(exclude={'items'})
            
            # Create order
            order = Order(
                tenant_id=tenant_id,
                order_number=order_number,
                order_status="pending",
                payment_status="unpaid",
                **order_dict,
                order_owner_id=user_id,
                created_by=user_id,
                updated_by=user_id
            )
            
            db.add(order)
            db.flush()  # Get order ID
            
            # Create order items
            for item_data in items_data:
                item = OrderItem(
                    order_id=order.id,
                    **item_data.dict()
                )
                db.add(item)
            
            db.commit()
            db.refresh(order)
            
            # Load items
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            
            result = model_to_dict(order)
            result['items'] = [model_to_dict(item) for item in order_items]
            
            return {
                "success": True,
                "message": "Order created successfully",
                "data": result
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "ORDER_CREATE_FAILED",
                    "message": f"Failed to create order: {str(e)}"
                }
            }
    
    @staticmethod
    def get_order(
        db: Session,
        order_id: UUID,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get order by ID with items"""
        try:
            order = db.query(Order).filter(
                Order.id == order_id,
                Order.tenant_id == tenant_id,
                Order.is_deleted == False
            ).first()
            
            if not order:
                return {
                    "success": False,
                    "error": {
                        "code": "ORDER_NOT_FOUND",
                        "message": "Order not found"
                    }
                }
            
            # Load items
            items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            result = model_to_dict(order)
            result['items'] = [model_to_dict(item) for item in items]
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "ORDER_GET_FAILED",
                    "message": f"Failed to get order: {str(e)}"
                }
            }
    
    @staticmethod
    def list_orders(
        db: Session,
        tenant_id: str,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        order_status: Optional[str] = None,
        payment_status: Optional[str] = None,
        account_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """List orders with filters and pagination"""
        try:
            query = db.query(Order).filter(
                Order.tenant_id == tenant_id,
                Order.is_deleted == False
            )
            
            if search:
                search_filter = f"%{search}%"
                query = query.filter(Order.order_number.ilike(search_filter))
            
            if order_status:
                query = query.filter(Order.order_status == order_status)
            
            if payment_status:
                query = query.filter(Order.payment_status == payment_status)
            
            if account_id:
                query = query.filter(Order.account_id == account_id)
            
            total = query.count()
            orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
            
            # Load items for each order
            results = []
            for order in orders:
                order_dict = model_to_dict(order)
                items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
                order_dict['items'] = [model_to_dict(item) for item in items]
                results.append(order_dict)
            
            return {
                "success": True,
                "data": {
                    "orders": results,
                    "total": total,
                    "page": skip // limit + 1,
                    "page_size": limit,
                    "total_pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "ORDER_LIST_FAILED",
                    "message": f"Failed to list orders: {str(e)}"
                }
            }
    
    @staticmethod
    def update_order(
        db: Session,
        order_id: UUID,
        order_data: OrderUpdate,
        tenant_id: str,
        user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Update order"""
        try:
            order = db.query(Order).filter(
                Order.id == order_id,
                Order.tenant_id == tenant_id,
                Order.is_deleted == False
            ).first()
            
            if not order:
                return {
                    "success": False,
                    "error": {
                        "code": "ORDER_NOT_FOUND",
                        "message": "Order not found"
                    }
                }
            
            update_data = order_data.dict(exclude_unset=True)
            
            # Update balance if paid amount changed
            if 'paid_amount' in update_data:
                order.paid_amount = update_data['paid_amount']
                order.balance_amount = order.total_amount - order.paid_amount
                
                # Update payment status
                if order.balance_amount <= 0:
                    order.payment_status = "paid"
                elif order.paid_amount > 0:
                    order.payment_status = "partial"
            
            for field, value in update_data.items():
                if field != 'paid_amount':  # Already handled above
                    setattr(order, field, value)
            
            order.updated_by = user_id
            order.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(order)
            
            # Load items
            items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
            
            result = model_to_dict(order)
            result['items'] = [model_to_dict(item) for item in items]
            
            return {
                "success": True,
                "message": "Order updated successfully",
                "data": result
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": {
                    "code": "ORDER_UPDATE_FAILED",
                    "message": f"Failed to update order: {str(e)}"
                }
            }
