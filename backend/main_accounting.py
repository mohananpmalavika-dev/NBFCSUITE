"""
NBFC Financial Suite - Accounting Service
Microservice Architecture - Financial Accounting Module

This service handles:
- Chart of Accounts
- Journal Entries
- General Ledger
- Trial Balance & Financial Reports
- Fixed Assets Management
- TDS & GST Compliance
- Vendor Payments

Memory Footprint: ~180MB
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


def import_accounting_models():
    """Import only Accounting service models"""
    logger.info("📦 Loading Accounting Service models...")
    
    # 1. Core models (REQUIRED for auth)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission
    )
    
    # 2. Accounting Core models
    from backend.shared.database.accounting_models import (
        ChartOfAccounts, JournalEntry, JournalEntryLine, GeneralLedger,
        TrialBalance, AccountingPeriod
    )
    
    # 3. Accounting Extended models (Vendors, Payments)
    from backend.shared.database.accounting_extended_models import (
        PurchaseInvoice, VendorPayment, VendorPaymentAllocation
    )
    
    # 4. Vendor model from procurement (needed for vendor payments)
    from backend.shared.database.procurement_models import Vendor
    
    # 5. Fixed Assets (if enabled)
    if settings.ENABLE_FIXED_ASSETS:
        from backend.shared.database.asset_models import (
            FixedAsset, AssetDepreciation, AssetMaintenance, AssetTransfer,
            AssetVerification, AssetVerificationCycle
        )
    
    logger.info("✅ Accounting Service models loaded")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting NBFC Accounting Service...")
    logger.info(f"Service: ACCOUNTING (GL, Assets, Reports, Compliance)")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database: Shared PostgreSQL")
    
    # Import models
    import_accounting_models()
    
    # Skip table creation (tables are managed centrally)
    skip_table_creation = os.getenv("SKIP_TABLE_CREATION", "true").lower() == "true"
    
    if skip_table_creation:
        logger.info("⏭️  SKIP_TABLE_CREATION=true: Using existing database schema")
    else:
        logger.info("🔧 Creating tables for Accounting service...")
        async with engine.begin() as conn:
            def create_tables_sync(sync_conn):
                Base.metadata.create_all(bind=sync_conn, checkfirst=True)
            await conn.run_sync(create_tables_sync)
        logger.info("✅ Tables created")
    
    logger.info("✅ Accounting Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Accounting Service...")
    await engine.dispose()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="NBFC Financial Suite - Accounting Service",
    description="Financial Accounting microservice: GL, Assets, Reports, Compliance",
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
    return {
        "success": True,
        "data": {
            "service": "NBFC Accounting Service",
            "version": "2.0.0-microservices",
            "status": "running",
            "modules": ["Chart of Accounts", "Journal Entries", "General Ledger", "Fixed Assets", "TDS/GST"],
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
            "service": "accounting"
        }
    }


# Load routers dynamically
def load_accounting_routers():
    """Load only Accounting service routers"""
    logger.info("📍 Loading Accounting service routers...")
    
    # Core Accounting
    from backend.services.accounting.router import router as accounting_router
    app.include_router(accounting_router, prefix="/api/accounting", tags=["Accounting"])
    
    # TDS
    from backend.services.accounting.tds_router import router as tds_router
    app.include_router(tds_router, prefix="/api/accounting", tags=["TDS"])
    
    # GST
    from backend.services.accounting.gst_router import router as gst_router
    app.include_router(gst_router, prefix="/api/accounting", tags=["GST"])
    
    # Fixed Assets (if enabled)
    if settings.ENABLE_FIXED_ASSETS:
        logger.info("Loading Fixed Assets routers...")
        from backend.services.accounting.asset_router import router as asset_router
        app.include_router(asset_router, prefix="/api/accounting", tags=["Fixed Assets"])
    
    logger.info("✅ Accounting service routers loaded")


# Load routers
load_accounting_routers()

logger.info("✅ Accounting Service initialized and ready")
