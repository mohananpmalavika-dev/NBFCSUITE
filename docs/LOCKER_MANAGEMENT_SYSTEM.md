# Locker Management System - Complete Implementation

## Overview

The Locker Management System is a comprehensive module for managing bank locker operations including inventory management, customer allocations, rent collection, and analytics.

## Architecture

### Backend Structure
```
backend/
├── shared/
│   ├── database/
│   │   └── locker_models.py          # 5 database models (500 lines)
│   ├── config.py                      # Feature flag configuration
│   └── conditional_imports.py         # Module registration
└── services/
    └── locker/
        ├── __init__.py                # Package initialization
        ├── schemas.py                 # 40+ Pydantic schemas (900 lines)
        ├── locker_service.py          # Inventory service (450 lines)
        ├── allocation_service.py      # Allocation service (550 lines)
        ├── payment_service.py         # Payment service (400 lines)
        └── router.py                  # 30+ API endpoints (700 lines)
```

### Frontend Structure
```
frontend/apps/admin-portal/src/
├── services/
│   └── locker.service.ts             # TypeScript API client (400 lines)
└── app/
    └── lockers/
        ├── layout.tsx                # Navigation layout
        ├── page.tsx                  # Redirect to dashboard
        ├── master/
        │   └── page.tsx              # Locker inventory management (500 lines)
        ├── allocations/
        │   └── page.tsx              # Customer allocations (750 lines)
        ├── payments/
        │   └── page.tsx              # Rent collection (650 lines)
        └── dashboard/
            └── page.tsx              # Analytics dashboard (850 lines)
```

## Database Models

### 1. LockerMaster
Manages locker inventory and specifications.

**Fields:**
- `id`: Primary key
- `locker_number`: Unique locker identifier
- `size`: Enum (SMALL, MEDIUM, LARGE, EXTRA_LARGE)
- `location`: Physical location details
- `branch`: Branch assignment
- `vault_room`, `floor`, `rack_number`: Physical positioning
- `locker_type`: Single or dual key system
- `status`: Enum (AVAILABLE, ALLOCATED, MAINTENANCE, BLOCKED)
- `annual_rent`: Base rent amount
- `security_deposit`: Required deposit
- `lock_type`: Type of locking mechanism
- `installation_date`, `last_maintenance_date`: Maintenance tracking
- `tenant_id`: Multi-tenancy support
- `is_deleted`: Soft delete flag

### 2. LockerAllocation
Tracks customer-locker assignments.

**Fields:**
- `id`: Primary key
- `locker_id`: Foreign key to LockerMaster
- `customer_id`: Foreign key to customer
- `allocation_date`, `start_date`, `end_date`: Agreement period
- `status`: Enum (ACTIVE, EXPIRED, CLOSED, RENEWED)
- `annual_rent`: Agreed rent
- `security_deposit_amount`: Deposit collected
- `rent_frequency`: Payment frequency
- `customer_key_number`, `bank_key_number`: Key tracking
- `nominee_name`, `nominee_relationship`, `nominee_dob`, `nominee_percentage`: Nominee details
- `closure_date`, `closure_reason`: Closure tracking
- `deposit_refund_amount`, `refund_date`: Settlement details

### 3. LockerRentPayment
Records all rent and payment transactions.

**Fields:**
- `id`: Primary key
- `allocation_id`: Foreign key to LockerAllocation
- `payment_type`: Enum (RENT, SECURITY_DEPOSIT, PENALTY)
- `payment_mode`: Enum (CASH, CHEQUE, NEFT, RTGS, UPI, CARD)
- `amount`: Payment amount
- `payment_date`: Transaction date
- `period_from`, `period_to`: Rent period (for RENT type)
- `receipt_number`: Auto-generated receipt
- `cheque_number`, `cheque_date`, `bank_name`: Cheque details
- `transaction_reference`: UTR for digital payments
- `remarks`: Additional notes

### 4. LockerMaintenance
Tracks maintenance activities.

**Fields:**
- `id`: Primary key
- `locker_id`: Foreign key to LockerMaster
- `maintenance_date`: Date of maintenance
- `maintenance_type`: Type of work
- `description`: Work details
- `cost`: Maintenance cost
- `performed_by`: Technician/staff
- `next_maintenance_date`: Scheduled next maintenance

### 5. LockerAccessLog
Audit trail for locker access.

**Fields:**
- `id`: Primary key
- `allocation_id`: Foreign key to LockerAllocation
- `access_date`: Date/time of access
- `access_type`: Entry or exit
- `authorized_person`: Person accessing
- `staff_witness`: Witnessing staff member
- `remarks`: Additional notes

## API Endpoints

### Locker Master Management
- `GET /api/lockers` - List all lockers with filters
- `POST /api/lockers` - Create new locker
- `GET /api/lockers/{id}` - Get locker details
- `PUT /api/lockers/{id}` - Update locker
- `DELETE /api/lockers/{id}` - Delete locker (soft delete)
- `GET /api/lockers/available` - Get available lockers by size
- `GET /api/lockers/floor-plan` - Get floor plan layout
- `GET /api/lockers/occupancy-stats` - Get occupancy statistics

### Allocation Management
- `GET /api/lockers/allocations` - List allocations with filters
- `POST /api/lockers/allocations` - Create new allocation
- `GET /api/lockers/allocations/{id}` - Get allocation details
- `PUT /api/lockers/allocations/{id}` - Update allocation
- `POST /api/lockers/allocations/{id}/renew` - Renew allocation
- `POST /api/lockers/allocations/{id}/close` - Close allocation
- `GET /api/lockers/allocations/expiring` - Get expiring allocations
- `GET /api/lockers/allocations/overdue` - Get overdue payments
- `POST /api/lockers/allocations/calculate-rent` - Calculate rent amount

### Payment Management
- `GET /api/lockers/payments` - List payments with filters
- `POST /api/lockers/allocations/{id}/payments` - Record payment
- `GET /api/lockers/payments/{id}` - Get payment details
- `GET /api/lockers/allocations/{id}/payment-history` - Get payment history
- `GET /api/lockers/revenue-stats` - Get revenue statistics
- `GET /api/lockers/collection-efficiency` - Get collection metrics

### Dashboard & Analytics
- `GET /api/lockers/dashboard` - Get comprehensive dashboard data
- `GET /api/lockers/reports/inventory` - Generate inventory report
- `GET /api/lockers/reports/maintenance` - Generate maintenance report

## Frontend Features

### 1. Locker Master Page (`/lockers/master`)
**Features:**
- Statistics cards (total, available, allocated, occupancy rate)
- Search and filters by size and status
- Data table with locker details
- Create/Edit locker dialogs
- Real-time updates with React Query
- Responsive design

**Key Components:**
- Stats overview
- Search and filter bar
- Locker data table
- Create/Edit modal forms
- Toast notifications

### 2. Allocations Page (`/lockers/allocations`)
**Features:**
- Tabbed interface (All, Active, Expiring)
- Alert cards for critical items
- Allocation list with customer info
- Create allocation dialog with:
  - Customer and locker selection
  - Agreement period configuration
  - Financial terms setup
  - Key management
  - Nominee details form
- Renewal workflow
- Closure workflow with settlement calculation

**Key Components:**
- Tab navigation
- Alert banners
- Allocation data table
- Multi-step allocation form
- Renewal dialog
- Closure dialog with refund calculation

### 3. Payments Page (`/lockers/payments`)
**Features:**
- Revenue statistics cards
- Outstanding rent alerts
- Tabbed interface (Payment History, Outstanding Rent)
- Payment entry form with:
  - Allocation selection
  - Payment type and mode
  - Dynamic instrument details (cheque, UTR)
  - Period selection for rent
- Receipt preview and print
- Payment history with advanced filters
- Outstanding rent tracking with quick payment

**Key Components:**
- Revenue stats cards
- Payment history table with filters
- Outstanding rent table
- Payment entry dialog
- Receipt preview dialog
- Quick payment buttons

### 4. Dashboard Page (`/lockers/dashboard`)
**Features:**
- Key metrics overview
- Critical alerts section
- Four main tabs:
  - **Overview**: Occupancy pie chart, revenue trend, size distribution
  - **Occupancy Analytics**: Status distribution, size-wise breakdown, branch filtering
  - **Revenue Analytics**: Monthly trends, collection efficiency, payment breakdown
  - **Recent Activity**: Recent allocations, payments, expiring allocations

**Key Components:**
- Metric cards
- Alert banners
- Charts (Pie, Line, Bar using Recharts)
- Data tables
- Filter dropdowns
- Export functionality

## Service Layer

### LockerService
Manages locker inventory operations.

**Key Methods:**
- `get_lockers()`: List with pagination and filters
- `create_locker()`: Create new locker
- `update_locker()`: Update locker details
- `delete_locker()`: Soft delete
- `get_available_lockers()`: Get available by size
- `get_floor_plan()`: Get layout visualization
- `get_occupancy_stats()`: Calculate occupancy metrics
- `record_maintenance()`: Log maintenance
- `get_maintenance_history()`: Retrieve history

### AllocationService
Manages customer allocations lifecycle.

**Key Methods:**
- `create_allocation()`: Create new allocation
- `renew_allocation()`: Renew existing
- `close_allocation()`: Close and calculate settlement
- `calculate_rent()`: Calculate pro-rated rent
- `get_expiring_allocations()`: Get expiring soon
- `get_overdue_allocations()`: Get payment overdue
- `log_access()`: Record locker access

### PaymentService
Manages payment recording and analytics.

**Key Methods:**
- `record_payment()`: Record rent payment
- `get_payment_history()`: Get allocation payments
- `get_revenue_stats()`: Calculate revenue metrics
- `get_collection_efficiency()`: Calculate collection rate
- `generate_receipt()`: Generate receipt number

## Configuration

### Feature Flag
Enable/disable the module in `backend/shared/config.py`:

```python
ENABLE_LOCKER_MANAGEMENT = os.getenv("ENABLE_LOCKER_MANAGEMENT", "true").lower() == "true"
```

### Environment Variables
```bash
# Enable locker management module
ENABLE_LOCKER_MANAGEMENT=true
```

## Multi-Tenancy

All models include `tenant_id` for multi-tenant support:
- Automatic filtering by tenant in all queries
- Tenant isolation at database level
- Secure tenant-based access control

## Security Features

1. **Authentication**: All endpoints require authentication
2. **Authorization**: Role-based access control
3. **Tenant Isolation**: Automatic tenant filtering
4. **Soft Delete**: Data retention with `is_deleted` flag
5. **Audit Trail**: Created/updated timestamps and user tracking
6. **Access Logging**: Complete locker access audit trail

## Usage Examples

### Creating a Locker
```python
locker_data = {
    "locker_number": "L001",
    "size": "MEDIUM",
    "location": "Main Vault",
    "branch": "Main Branch",
    "vault_room": "Vault A",
    "floor": "Ground",
    "rack_number": "R1-S1",
    "locker_type": "dual_key",
    "annual_rent": 5000.00,
    "security_deposit": 10000.00,
}
locker = await locker_service.create_locker(locker_data, tenant_id, user_id)
```

### Creating an Allocation
```typescript
const allocationData = {
  customer_id: 123,
  locker_id: 456,
  allocation_date: "2024-01-01",
  start_date: "2024-01-01",
  end_date: "2024-12-31",
  annual_rent: 5000,
  security_deposit_amount: 10000,
  rent_frequency: "annual",
  customer_key_number: "CK001",
  bank_key_number: "BK001",
  nominee_name: "John Doe",
  nominee_relationship: "Spouse",
  nominee_dob: "1980-01-01",
  nominee_percentage: 100,
};
await lockerService.createAllocation(allocationData);
```

### Recording a Payment
```typescript
const paymentData = {
  allocation_id: 789,
  payment_type: PaymentType.RENT,
  payment_mode: PaymentMode.NEFT,
  amount: 5000,
  payment_date: "2024-06-01",
  period_from: "2024-01-01",
  period_to: "2024-12-31",
  transaction_reference: "UTR123456789",
};
await lockerService.recordPayment(789, paymentData);
```

## Statistics

### Code Statistics
- **Total Lines**: ~5,200 lines
- **Backend**: 3,550 lines
  - Models: 500 lines
  - Schemas: 900 lines
  - Services: 1,400 lines
  - Router: 700 lines
- **Frontend**: 2,650 lines
  - API Client: 400 lines
  - UI Pages: 2,750 lines
  - Layout: 100 lines

### Database Objects
- **Models**: 5 tables
- **Enums**: 6 types
- **Indexes**: Multi-column indexes on frequently queried fields
- **Relationships**: Proper foreign keys with cascading

### API Endpoints
- **Total Endpoints**: 30+
- **CRUD Operations**: 15 endpoints
- **Business Logic**: 10 endpoints
- **Analytics**: 5 endpoints

## Testing Recommendations

### Backend Tests
1. Model validation tests
2. Service layer unit tests
3. API endpoint integration tests
4. Business logic tests (rent calculation, occupancy stats)
5. Multi-tenancy isolation tests

### Frontend Tests
1. Component rendering tests
2. Form validation tests
3. API integration tests
4. User workflow tests
5. Responsive design tests

## Future Enhancements

1. **Mobile App**: Customer self-service app
2. **Biometric Access**: Fingerprint/facial recognition
3. **IoT Integration**: Smart locker monitoring
4. **Email Notifications**: Automated reminders for expiry/payment
5. **SMS Alerts**: Payment confirmations and alerts
6. **Advanced Analytics**: Predictive analytics for revenue
7. **Document Management**: Store customer documents
8. **QR Code**: QR-based locker access
9. **Waiting List**: Queue management for unavailable sizes
10. **Multi-Language**: Localization support

## Support

For issues or questions:
1. Check the API documentation
2. Review error logs in the backend
3. Verify feature flag is enabled
4. Check database migrations are applied
5. Validate tenant configuration

## License

Part of NBFC Suite - All Rights Reserved
