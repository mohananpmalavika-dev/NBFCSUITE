# CRM Sales Automation - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

This guide helps you quickly set up and test the CRM Sales Automation module.

---

## Prerequisites

- Backend server running on `http://localhost:8000`
- Frontend server running on `http://localhost:3000`
- Database with tables created
- At least one CRM Account created

---

## Quick Setup Checklist

### ✅ Backend Verification

1. **Check routes are registered:**
   ```bash
   # Open http://localhost:8000/docs
   # Look for these sections:
   - CRM - Product Catalog
   - CRM - Quote Generation
   - CRM - Order Management
   ```

2. **Verify database tables exist:**
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_name LIKE 'crm_%' 
   AND table_name IN ('crm_products', 'crm_quotes', 'crm_quote_items', 'crm_orders', 'crm_order_items');
   ```

3. **Test API endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/products
   # Should return: {"success": true, "data": {"products": [], ...}}
   ```

### ✅ Frontend Verification

1. **Check routes exist:**
   - http://localhost:3000/crm/products
   - http://localhost:3000/crm/quotes
   - http://localhost:3000/crm/orders

2. **Verify API service:**
   - Open browser console
   - Navigate to any CRM Sales page
   - Check for API calls in Network tab

---

## Sample Data Creation

### 1. Create a Sample Product

**Via API (Swagger UI):**
```json
POST /api/v1/products
{
  "name": "Premium Software License",
  "product_code": "PROD-001",
  "description": "Annual software license",
  "category": "software",
  "status": "active",
  "unit_price": 50000.00,
  "cost_price": 30000.00,
  "currency": "INR",
  "unit_of_measure": "license",
  "track_inventory": false,
  "hsn_sac_code": "998314",
  "tax_rate": 18.00
}
```

**Via Frontend:**
1. Go to http://localhost:3000/crm/products
2. Click "Add Product"
3. Fill in the form
4. Click "Create Product"

### 2. Create a Sample Quote

**Via API:**
```json
POST /api/v1/quotes
{
  "account_id": "your-account-uuid",
  "quote_date": "2025-01-15",
  "valid_until": "2025-02-15",
  "currency": "INR",
  "status": "draft",
  "items": [
    {
      "product_id": "your-product-uuid",
      "product_name": "Premium Software License",
      "description": "Annual license for 5 users",
      "quantity": 5,
      "unit_price": 50000.00,
      "discount_percentage": 10,
      "tax_rate": 18.00
    }
  ],
  "terms_conditions": "Payment within 30 days"
}
```

**Via Frontend:**
1. Go to http://localhost:3000/crm/quotes
2. Click "Create Quote"
3. Select account
4. Add items
5. Click "Create Quote"

### 3. Create a Sample Order

**From Quote:**
1. Open quote
2. Change status to "accepted"
3. Click "Convert to Order"

**Standalone:**
1. Go to http://localhost:3000/crm/orders
2. Click "Create Order"
3. Fill in details
4. Click "Create Order"

---

## Common Workflows

### Workflow 1: Product → Quote → Order

```
1. Create Product
   ↓
2. Create Quote with Product
   ↓
3. Send Quote (change status to "sent")
   ↓
4. Accept Quote (change status to "accepted")
   ↓
5. Convert Quote to Order
   ↓
6. Process Order (update status: confirmed → processing → shipped → delivered)
   ↓
7. Record Payment
```

### Workflow 2: Direct Order

```
1. Create Product
   ↓
2. Create Order directly
   ↓
3. Add payment information
   ↓
4. Process and ship order
```

---

## Testing Calculations

### Test Case 1: Basic Quote Calculation

**Input:**
- Product Price: ₹1,000
- Quantity: 10
- Tax Rate: 18%

**Expected Output:**
- Subtotal: ₹10,000
- Tax: ₹1,800
- Total: ₹11,800

### Test Case 2: Quote with Discount

**Input:**
- Product Price: ₹1,000
- Quantity: 10
- Discount: 10%
- Tax Rate: 18%

**Expected Output:**
- Subtotal: ₹10,000
- Discount: ₹1,000
- Taxable: ₹9,000
- Tax: ₹1,620
- Total: ₹10,620

### Test Case 3: Order Payment Status

**Test Unpaid:**
- Total: ₹10,000
- Paid: ₹0
- Status: UNPAID

**Test Partial:**
- Total: ₹10,000
- Paid: ₹5,000
- Status: PARTIAL

**Test Paid:**
- Total: ₹10,000
- Paid: ₹10,000
- Status: PAID

---

## API Endpoints Reference

### Products
```
GET    /api/v1/products              List all products
POST   /api/v1/products              Create product
GET    /api/v1/products/{id}         Get product
PUT    /api/v1/products/{id}         Update product
DELETE /api/v1/products/{id}         Delete product
```

### Quotes
```
GET    /api/v1/quotes                List all quotes
POST   /api/v1/quotes                Create quote
GET    /api/v1/quotes/{id}           Get quote
PUT    /api/v1/quotes/{id}           Update quote
DELETE /api/v1/quotes/{id}           Delete quote
```

### Orders
```
GET    /api/v1/orders                List all orders
POST   /api/v1/orders                Create order
GET    /api/v1/orders/{id}           Get order
PUT    /api/v1/orders/{id}           Update order
DELETE /api/v1/orders/{id}           Delete order
```

---

## Frontend Routes Reference

### Products
```
/crm/products                List view
/crm/products/new            Create form
/crm/products/{id}           Detail view
/crm/products/{id}/edit      Edit form
```

### Quotes
```
/crm/quotes                  List view
/crm/quotes/new              Create form
/crm/quotes/{id}             Detail view
/crm/quotes/{id}/edit        Edit form
```

### Orders
```
/crm/orders                  List view
/crm/orders/new              Create form
/crm/orders/new?quote={id}   Create from quote
/crm/orders/{id}             Detail view
/crm/orders/{id}/edit        Edit form
```

---

## Troubleshooting Quick Fixes

### Issue: Can't see products in quote builder
**Fix:** Create at least one product with status "active"

### Issue: Quote calculations seem wrong
**Fix:** Check that tax_rate is set on products

### Issue: Can't convert quote to order
**Fix:** Set quote status to "accepted" first

### Issue: Payment status not updating
**Fix:** Edit order and update paid_amount field

### Issue: API returns 404
**Fix:** Verify routes are registered in backend/main.py

### Issue: Frontend page blank
**Fix:** Check browser console for errors, verify API is reachable

---

## Next Steps

1. ✅ Create sample products
2. ✅ Create test quotes
3. ✅ Convert quotes to orders
4. ✅ Test calculations
5. ✅ Verify all CRUD operations
6. ✅ Test search and filters
7. ✅ Check print preview
8. ✅ Test responsive design

---

## Support & Documentation

- **Full Documentation:** `docs/CRM_SALES_AUTOMATION_IMPLEMENTATION.md`
- **API Docs:** http://localhost:8000/docs
- **Component Storybook:** (if available)

---

## Quick Command Reference

### Start Backend
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend/apps/admin-portal
npm run dev
```

### Check Logs
```bash
# Backend
tail -f backend/logs/app.log

# Frontend
# Check browser console
```

### Database Check
```bash
# PostgreSQL
psql -U postgres -d nbfc_db
\dt crm_*
```

---

**Happy Coding! 🎉**

Last Updated: January 2025
