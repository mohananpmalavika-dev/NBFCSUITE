"""
NBFC Financial Suite - Core Service
Microservice Architecture - Core Business Module

This service handles:
- Authentication & Authorization
- Customer Management (CIF)
- Loan Origination & Management
- Master Data Management
- Dashboard & Analytics

Memory Footprint: ~250MB
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


def import_core_models():
    """Import only Core service models"""
    logger.info("📦 Loading Core Service models...")
    
    # 1. Core models (ESSENTIAL)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission, FileUpload
    )
    
    # 2. Master data models (ESSENTIAL)
    from backend.shared.database.master_data_models import (
        Country, State, City, Pincode, Bank, BankBranch, Currency,
        InterestRateType, LoanProductType, DocumentType, Occupation,
        Industry, LoanPurpose, RelationshipType, Holiday, FinancialYear
    )
    
    # 3. Customer models (CORE BUSINESS)
    from backend.shared.database.customer_models import (
        Customer, CustomerKYC, CustomerDocument, CustomerFamily, 
        CustomerBankAccount, CustomerReference, CustomerTimeline,
        CustomerBureauHistory, ActivityType, BureauProvider, BureauPullStatus
    )
    
    # 4. Loan models (CORE BUSINESS)
    from backend.shared.database.loan_models import (
        LoanProduct, LoanApplication, LoanApplicationCoApplicant,
        LoanApplicationDocument, LoanApprovalWorkflow, LoanAccount,
        LoanEMISchedule, LoanRepayment, LoanStatus, ApplicationStatus,
        RepaymentFrequency, EMIStatus
    )
    
    logger.info("✅ Core Service models loaded")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting NBFC Core Service...")
    logger.info(f"Service: CORE (Auth, Customers, Loans, MasterData)")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database: Shared PostgreSQL")
    
    # Import models
    import_core_models()
    
    # Skip table creation (tables are managed centrally)
    skip_table_creation = os.getenv("SKIP_TABLE_CREATION", "true").lower() == "true"
    
    if skip_table_creation:
        logger.info("⏭️  SKIP_TABLE_CREATION=true: Using existing database schema")
    else:
        logger.info("🔧 Creating tables for Core service...")
        async with engine.begin() as conn:
            def create_tables_sync(sync_conn):
                Base.metadata.create_all(bind=sync_conn, checkfirst=True)
            await conn.run_sync(create_tables_sync)
        logger.info("✅ Tables created")
    
    logger.info("✅ Core Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Core Service...")
    await engine.dispose()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="NBFC Financial Suite - Core Service",
    description="Core business microservice: Auth, Customers, Loans, MasterData",
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
            "service": "NBFC Core Service",
            "version": "2.0.0-microservices",
            "status": "running",
            "modules": ["Auth", "Customers", "Loans", "MasterData", "Dashboard"],
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
            "service": "core"
        }
    }


# Load routers dynamically
def load_core_routers():
    """Load only Core service routers"""
    logger.info("📍 Loading Core service routers...")
    
    # Auth
    from backend.services.auth.router import router as auth_router
    app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
    
    # Dashboard
    from backend.services.dashboard.router import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
    
    # Master Data
    from backend.services.masterdata.router import router as masterdata_router
    app.include_router(masterdata_router, prefix="/api/masterdata", tags=["Master Data"])
    
    # Customers
    from backend.services.customer.router import router as customer_router
    app.include_router(customer_router, prefix="/api/customers", tags=["Customers"])
    
    from backend.services.customer.timeline_router import router as timeline_router
    app.include_router(timeline_router, prefix="/api/customers", tags=["Customer Timeline"])
    
    # Loans
    from backend.services.loan import router as loan_router
    app.include_router(loan_router, prefix="/api/loans", tags=["Loans"])
    
    # File Upload
    from backend.services.file_upload.router import router as file_router
    app.include_router(file_router, prefix="/api/files", tags=["File Upload"])
    
    logger.info("✅ Core service routers loaded")


# Load routers
load_core_routers()

logger.info("✅ Core Service initialized and ready")
