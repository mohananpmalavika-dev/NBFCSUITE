"""
NBFC Financial Suite - Operations Service
Microservice Architecture - Business Operations Module

This service handles:
- CRM (Leads, Accounts, Opportunities, Sales)
- Treasury Management
- Compliance & Regulatory Reporting
- Risk Management
- ALM (Asset Liability Management)
- Branch Operations

Memory Footprint: ~220MB
Database: Shared PostgreSQL (all services use same DB)
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import os

from backend.shared.config import settings
from backend.shared.database.connection import engine, Base
from backend.shared.middleware.tenant import TenantMiddleware
from backend.shared.middleware.logging import LoggingMiddleware
from backend.shared.middleware.error_handler import ErrorHandlerMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def import_operations_models():
    """Import only Operations service models"""
    logger.info("📦 Loading Operations Service models...")
    
    # 1. Core models (REQUIRED for auth)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission
    )
    
    # 2. Vendor model (ALWAYS IMPORTED - shared across services)
    from backend.shared.database.procurement_models import Vendor
    
    # 3. CRM models (if enabled)
    if settings.ENABLE_CRM:
        logger.info("Importing CRM models...")
        from backend.shared.database.crm_lead_models import (
            Lead, LeadFollowUp, LeadActivity, LeadScoringRule, LeadAssignmentRule
        )
        from backend.shared.database.crm_account_models import (
            CRMAccount, CRMContact, CRMAccountRelationship, CRMActivity
        )
        from backend.shared.database.crm_marketing_models import (
            MarketingCampaign, CustomerSegment, SegmentMember, LandingPage,
            CampaignExecution, LandingPageSubmission, CampaignTemplate
        )
        
        if settings.ENABLE_CRM_OPPORTUNITIES:
            from backend.shared.database.crm_opportunity_models import (
                CRMOpportunity, CRMOpportunityProduct, CRMOpportunityActivity, CRMPipelineStageConfig
            )
        
        if settings.ENABLE_CRM_SALES:
            from backend.shared.database.crm_sales_models import (
                Product, Quote, QuoteItem, Order, OrderItem
            )
        
        if settings.ENABLE_CRM_SERVICE:
            from backend.shared.database.crm_service_models import (
                Ticket, TicketComment, TicketAttachment,
                KnowledgeArticle, ArticleAttachment,
                SLA, SLAViolation
            )
    
    # 4. Treasury models (if enabled)
    if settings.ENABLE_TREASURY:
        logger.info("Importing Treasury models...")
        from backend.shared.database.treasury_models import (
            TreasuryBankAccount, TreasuryCashPosition, BankStatement,
            BankReconciliation, ReconciliationItem, FundTransfer,
            LiquidityPosition, Investment, InvestmentTransaction, CashFlowForecast
        )
    
    # 5. ALM models (if enabled)
    if settings.ENABLE_ALM:
        logger.info("Importing ALM models...")
        from backend.shared.database.alm_models import (
            MaturityLadder, GapAnalysis, LiquidityRatio, InterestRateRisk,
            QuarterlyReturn, ALMLimits, ALMAlert
        )
    
    # 6. Compliance models (if enabled)
    if settings.ENABLE_COMPLIANCE:
        logger.info("Importing Compliance models...")
        from backend.shared.database.compliance_models import (
            CRILCBorrower, CRILCFacility, CRILCQuarterlyReturn,
            SMATracking, SMAStatusHistory, SMAQuarterlyReport, ComplianceAlert
        )
    
    # 7. Risk Management models (if enabled)
    if settings.ENABLE_RISK_MANAGEMENT:
        logger.info("Importing Risk Management models...")
        from backend.shared.database.risk_models import (
            CreditPolicy, RiskPricingRule, ExposureLimit, ExposureTransaction,
            RiskRating, EarlyWarningSignal, EarlyWarningAlert
        )
    
    # 8. Branch models (if enabled)
    if settings.ENABLE_BRANCH:
        logger.info("Importing Branch models...")
        from backend.shared.database.branch_models import (
            Organization, Branch, BranchDayOperation, BranchCounter,
            CashTransaction, CashDenomination, CashPosition,
            BranchPerformance, BranchTarget, BranchAuditLog
        )
    
    # 9. Integration models (if enabled)
    if settings.ENABLE_BUREAU_INTEGRATION or settings.ENABLE_BANK_STATEMENT or settings.ENABLE_OCR or settings.ENABLE_EKYC or settings.ENABLE_DIGILOCKER:
        logger.info("Importing Integration models...")
        from backend.shared.database.integration_models import (
            BureauReport, BureauConsent, BankStatementAnalysis,
            DocumentOCRResult, EKYCRecord, DigiLockerDocument
        )
    
    logger.info("✅ Operations Service models loaded")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting NBFC Operations Service...")
    logger.info(f"Service: OPERATIONS (CRM, Treasury, Compliance, Risk)")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database: Shared PostgreSQL")
    
    # Import models
    import_operations_models()
    
    # Skip table creation (tables are managed centrally)
    skip_table_creation = os.getenv("SKIP_TABLE_CREATION", "true").lower() == "true"
    
    if skip_table_creation:
        logger.info("⏭️  SKIP_TABLE_CREATION=true: Using existing database schema")
    else:
        logger.info("🔧 Creating tables for Operations service...")
        async with engine.begin() as conn:
            def create_tables_sync(sync_conn):
                Base.metadata.create_all(bind=sync_conn, checkfirst=True)
            await conn.run_sync(create_tables_sync)
        logger.info("✅ Tables created")
    
    logger.info("✅ Operations Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Operations Service...")
    await engine.dispose()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="NBFC Financial Suite - Operations Service",
    description="Business Operations microservice: CRM, Treasury, Compliance, Risk, ALM",
    version="2.0.0-microservices",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Configuration
logger.info("🌐 Configuring CORS to allow ALL origins...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
logger.info("✅ CORS configured: allow_origins=['*']")

# Other middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
if settings.TENANT_ISOLATION_ENABLED:
    app.add_middleware(TenantMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.APP_DEBUG else None
            }
        }
    )


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    modules = []
    if settings.ENABLE_CRM:
        modules.append("CRM")
    if settings.ENABLE_TREASURY:
        modules.append("Treasury")
    if settings.ENABLE_ALM:
        modules.append("ALM")
    if settings.ENABLE_COMPLIANCE:
        modules.append("Compliance")
    if settings.ENABLE_RISK_MANAGEMENT:
        modules.append("Risk Management")
    if settings.ENABLE_BRANCH:
        modules.append("Branch Operations")
    
    return {
        "success": True,
        "data": {
            "service": "NBFC Operations Service",
            "version": "2.0.0-microservices",
            "status": "running",
            "modules": modules,
            "architecture": "microservices",
            "database": "shared-postgresql"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "operations"
        }
    }


# Load routers dynamically
def load_operations_routers():
    """Load only Operations service routers"""
    logger.info("📍 Loading Operations service routers...")
    
    # CRM (if enabled)
    if settings.ENABLE_CRM:
        logger.info("Loading CRM routers...")
        from backend.services.crm.account_router import router as crm_account_router
        from backend.services.crm.contact_router import router as crm_contact_router
        app.include_router(crm_account_router, prefix="/api/crm", tags=["CRM - Accounts"])
        app.include_router(crm_contact_router, prefix="/api/crm", tags=["CRM - Contacts"])
        
        if settings.ENABLE_CRM_OPPORTUNITIES:
            from backend.services.crm.opportunity_router import router as crm_opportunity_router
            app.include_router(crm_opportunity_router, prefix="/api/crm", tags=["CRM - Opportunities"])
        
        if settings.ENABLE_CRM_SALES:
            from backend.services.crm.sales_router import router as crm_sales_router
            app.include_router(crm_sales_router, prefix="/api/crm", tags=["CRM - Sales"])
        
        if settings.ENABLE_CRM_SERVICE:
            from backend.services.crm.service_router import router as crm_service_router
            app.include_router(crm_service_router, prefix="/api/crm", tags=["CRM - Service"])
    
    # Treasury (if enabled)
    if settings.ENABLE_TREASURY:
        logger.info("Loading Treasury routers...")
        from backend.services.treasury.bank_account_router import router as treasury_bank_account_router
        from backend.services.treasury.cash_position_router import router as treasury_cash_position_router
        from backend.services.treasury.reconciliation_router import router as treasury_reconciliation_router
        from backend.services.treasury.fund_transfer_router import router as treasury_fund_transfer_router
        app.include_router(treasury_bank_account_router, prefix="/api/treasury", tags=["Treasury - Bank Accounts"])
        app.include_router(treasury_cash_position_router, prefix="/api/treasury", tags=["Treasury - Cash Position"])
        app.include_router(treasury_reconciliation_router, prefix="/api/treasury", tags=["Treasury - Reconciliation"])
        app.include_router(treasury_fund_transfer_router, prefix="/api/treasury", tags=["Treasury - Fund Transfers"])
    
    # ALM (if enabled)
    if settings.ENABLE_ALM:
        logger.info("Loading ALM routers...")
        from backend.services.treasury.alm_router import router as alm_router
        app.include_router(alm_router, prefix="/api/treasury/alm", tags=["ALM"])
    
    # Compliance (if enabled)
    if settings.ENABLE_COMPLIANCE:
        logger.info("Loading Compliance routers...")
        from backend.services.compliance.router import router as compliance_router
        app.include_router(compliance_router, prefix="/api/compliance", tags=["Compliance"])
    
    # Risk Management (if enabled)
    if settings.ENABLE_RISK_MANAGEMENT:
        logger.info("Loading Risk Management routers...")
        from backend.services.risk.router import router as risk_router
        app.include_router(risk_router, prefix="/api/risk", tags=["Risk Management"])
    
    # Branch Operations (if enabled)
    if settings.ENABLE_BRANCH:
        logger.info("Loading Branch routers...")
        from backend.services.branch import (
            organization_router as branch_organization_router, 
            branch_router, 
            day_operation_router, 
            cash_router, 
            performance_router
        )
        app.include_router(branch_organization_router, prefix="/api/branch", tags=["Branch - Organization"])
        app.include_router(branch_router, prefix="/api/branch", tags=["Branch - Management"])
        app.include_router(day_operation_router, prefix="/api/branch", tags=["Branch - Operations"])
        app.include_router(cash_router, prefix="/api/branch", tags=["Branch - Cash Management"])
        app.include_router(performance_router, prefix="/api/branch", tags=["Branch - Performance"])
    
    # Integration services (if enabled)
    if settings.ENABLE_BUREAU_INTEGRATION:
        logger.info("Loading Bureau Integration routers...")
        from backend.services.integration.bureau_router import router as bureau_integration_router
        app.include_router(bureau_integration_router, prefix="/api/integration", tags=["Integration - Bureau"])
    
    if settings.ENABLE_BANK_STATEMENT:
        logger.info("Loading Bank Statement Analysis routers...")
        from backend.services.integration.bank_statement_router import router as bank_statement_router
        app.include_router(bank_statement_router, prefix="/api/integration", tags=["Integration - Bank Statement"])
    
    if settings.ENABLE_OCR:
        logger.info("Loading OCR routers...")
        from backend.services.integration.ocr_router import router as ocr_router
        app.include_router(ocr_router, prefix="/api/integration", tags=["Integration - OCR"])
    
    logger.info("✅ Operations service routers loaded")


# Load routers
load_operations_routers()

logger.info("✅ Operations Service initialized and ready")
