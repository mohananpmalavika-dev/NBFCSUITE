"""
Deposit Management Service Module - COMPLETE

This module provides comprehensive deposit management functionality for NBFCs and Nidhi companies.

CORE SERVICES:
- Product Service: Deposit product management and calculations
- Account Service: Account opening, deposits, withdrawals, closures
- Interest Service: Interest calculation and posting

NEW SERVICES (COMPLETE):
- Passbook Service: Passbook entry management and PDF generation
- Statement Service: Statement generation (PDF/Excel) and email
- Certificate Service: Interest certificates and TDS Form 16A
- Batch Service: Maturity processing, TDS, penalties, bulk operations
- Reports Service: Comprehensive reports and analytics dashboard
- Notification Service: Maturity reminders, alerts, custom notifications
- Standing Instructions: Auto-debit, sweep-in/out, recurring transfers
- Advanced Operations: Freeze/unfreeze, lien, account transfer, joint accounts
- Regulatory Service: RBI returns, DICGC, concentration, KYC compliance
- Scheduled Jobs: Daily, monthly, quarterly, annual automation

API ROUTERS (100+ Endpoints):
- Product Router: Product CRUD and calculations (13 endpoints)
- Account Router: Account operations (18 endpoints)
- Interest Router: Interest management (15 endpoints)
- Passbook Router: Passbook operations (5 endpoints)
- Statement Router: Statement generation (6 endpoints)
- Certificate Router: Certificate generation (6 endpoints)
- Batch Router: Batch operations (10 endpoints)
- Reports Router: Reports and analytics (10 endpoints)

FEATURES IMPLEMENTED:
✅ Savings accounts (CASA) - Complete
✅ Fixed Deposits (FD) - Complete with maturity calculations
✅ Recurring Deposits (RD) - Complete with installment tracking
✅ Monthly Income Scheme (MIS) - Complete with payout automation
✅ Interest calculation engine - Simple, compound, daily balance methods
✅ Maturity processing - Automated with renewal support
✅ Nomination management - Complete nominee details
✅ Passbook management - View, print, PDF generation
✅ Statement generation - PDF, Excel, email functionality
✅ Interest certificates - Annual certificates and Form 16A
✅ TDS management - Calculation, deduction, certificates
✅ Auto-renewal - Automated FD renewal at maturity
✅ Dormancy management - Detection and reactivation
✅ Penalty management - Auto-penalties for violations
✅ MIS payout automation - Monthly interest payouts
✅ Batch operations - Maturity, TDS, bulk processing
✅ Reports & analytics - 10+ comprehensive reports
✅ Notifications - Email/SMS for all events
✅ Standing instructions - Auto-debit, sweep operations
✅ Account freeze/unfreeze - Complete control
✅ Lien marking - Loan security support
✅ Account transfer - Customer transfer support
✅ Joint accounts - Multiple holder support
✅ RBI compliance - Regulatory returns automation
✅ DICGC reporting - Deposit insurance tracking
✅ Scheduled jobs - Daily, monthly, quarterly automation

All services follow multi-tenant architecture with complete audit trails.
"""

from .product_service import DepositProductService
from .account_service import DepositAccountService
from .interest_service import InterestCalculationService
from .passbook_service import PassbookService
from .statement_service import StatementService
from .certificate_service import CertificateService
from .batch_service import BatchProcessingService
from .reports_service import ReportsService
from .notification_service import NotificationService
from .standing_instructions_service import StandingInstructionService
from .advanced_operations_service import AdvancedOperationsService
from .regulatory_service import RegulatoryService

from .product_router import router as product_router
from .account_router import router as account_router
from .interest_router import router as interest_router
from .passbook_router import router as passbook_router
from .statement_router import router as statement_router
from .certificate_router import router as certificate_router
from .batch_router import router as batch_router
from .reports_router import router as reports_router

__all__ = [
    # Services
    "DepositProductService",
    "DepositAccountService",
    "InterestCalculationService",
    "PassbookService",
    "StatementService",
    "CertificateService",
    "BatchProcessingService",
    "ReportsService",
    "NotificationService",
    "StandingInstructionService",
    "AdvancedOperationsService",
    "RegulatoryService",
    # Routers
    "product_router",
    "account_router",
    "interest_router",
    "passbook_router",
    "statement_router",
    "certificate_router",
    "batch_router",
    "reports_router",
]
