"""
NBFC Financial Suite - Minimal Application (Memory Optimized for Free Tier)
Core Modules Only: Auth, Dashboard, Customers, Loans, Master Data
Version: 1.0.2 - Memory Optimized
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import asyncio
import time
import logging
import os
from typing import Dict, Any

from sqlalchemy import inspect, text

from backend.shared.config import settings
from backend.shared.database.connection import engine, Base
from backend.shared.middleware.tenant import TenantMiddleware
from backend.shared.middleware.logging import LoggingMiddleware
from backend.shared.middleware.error_handler import ErrorHandlerMiddleware

# ============================================================================
# MINIMAL MODEL IMPORTS - ONLY CORE MODULES
# This reduces memory usage from ~525MB to ~200MB
# ============================================================================

# 1. Core models (ESSENTIAL - Always loaded)
from backend.shared.database.models import (
    Tenant, User, Role, UserRole, Permission, RolePermission, FileUpload
)

# 2. Master data models (ESSENTIAL - Required for all operations)
from backend.shared.database.master_data_models import (
    Country, State, City, Pincode, Bank, BankBranch, Currency,
    InterestRateType, LoanProductType, DocumentType, Occupation,
    Industry, LoanPurpose, RelationshipType, Holiday, FinancialYear
)

# 3. Customer models (CORE BUSINESS - Customer management)
from backend.shared.database.customer_models import (
    Customer, CustomerKYC, CustomerDocument, CustomerFamily, 
    CustomerBankAccount, CustomerReference, CustomerTimeline,
    CustomerBureauHistory, ActivityType, BureauProvider, BureauPullStatus
)

# 4. Loan models (CORE BUSINESS - Loan origination and management)
from backend.shared.database.loan_models import (
    LoanProduct, LoanApplication, LoanApplicationCoApplicant,
    LoanApplicationDocument, LoanApprovalWorkflow, LoanAccount,
    LoanEMISchedule, LoanRepayment, LoanStatus, ApplicationStatus,
    RepaymentFrequency, EMIStatus
)

# NOTE: All other modules (HRMS, CRM, Treasury, Compliance, etc.) are NOT loaded
# This saves ~300MB of memory. You can add them back later by:
# 1. Using the full main.py, OR
# 2. Adding specific modules here as needed

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting NBFC Financial Suite API (MINIMAL MODE)...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Modules Loaded: Core, MasterData, Customers, Loans ONLY")
    logger.info(f"Multi-tenant: {settings.TENANT_ISOLATION_ENABLED}")
    
    # Force create all tables on startup
    logger.info("🔄 Creating database tables...")
    logger.info(f"📊 Registered tables ({len(Base.metadata.tables)})")

    # Check if we should drop and recreate all tables
    force_recreate = os.getenv("DROP_ALL_TABLES", "false").lower() == "true"
    
    if force_recreate:
        logger.warning("⚠️ DROP_ALL_TABLES=true: Dropping all tables and recreating...")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("✅ All tables dropped")
        except Exception as drop_error:
            logger.warning(f"Could not drop tables: {drop_error}")
    
    # Create tables
    logger.info("🔧 Attempting to create database tables...")
    
    try:
        async with engine.begin() as conn:
            def create_tables_sync(sync_conn):
                logger.info("Executing Base.metadata.create_all...")
                Base.metadata.create_all(bind=sync_conn, checkfirst=True)
                logger.info("✅ Base.metadata.create_all completed successfully")
            
            await conn.run_sync(create_tables_sync)
            
        logger.info("✅ Table creation transaction committed")
        
    except Exception as create_error:
        error_msg = str(create_error).lower()
        logger.error(f"⚠️ Exception during table creation: {create_error}")
        
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            logger.warning(f"⚠️ Got 'already exists' error - tables may already exist")
            logger.info("⚠️ Continuing despite 'already exists' message...")
        else:
            logger.error(f"❌ Unexpected error creating tables")
            raise
    
    # Verify tables exist
    logger.info("🔍 Verifying tables were created...")
    await asyncio.sleep(1)
    
    try:
        async with engine.connect() as conn:
            def get_tables(sync_conn):
                inspector = inspect(sync_conn)
                tables = inspector.get_table_names(schema='public')
                return tables
            
            existing_tables = await conn.run_sync(get_tables)
        
        logger.info(f"✅ Database has {len(existing_tables)} tables")
        
        if not existing_tables:
            raise RuntimeError("No tables found in database after creation attempt")
        
        if "users" not in existing_tables:
            logger.error(f"❌ Users table missing from {len(existing_tables)} tables")
            raise RuntimeError("Database created, but users table is still missing")
        
        logger.info("✅ Database verification successful")
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down NBFC Financial Suite API...")
    await engine.dispose()
    logger.info("✅ Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME + " (Minimal)",
    description="NBFC Financial Suite - Memory Optimized Version (Core Modules Only)",
    version="1.0.2-minimal",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(TenantMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        }
        if "ctx" in error:
            error_dict["ctx"] = {k: str(v) for k, v in error["ctx"].items()}
        errors.append(error_dict)
    
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


# ============================================
# HEALTH CHECK ENDPOINTS
# ============================================

@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "success": True,
        "data": {
            "name": settings.APP_NAME + " (Minimal)",
            "version": "1.0.2-minimal",
            "status": "running",
            "environment": settings.APP_ENV,
            "docs": "/docs",
            "mode": "memory-optimized",
            "loaded_modules": ["Auth", "Dashboard", "MasterData", "Customers", "Loans"],
            "memory_note": "This is a minimal version with only core modules to fit free tier memory limits"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "timestamp": time.time(),
            "mode": "minimal",
            "services": {
                "api": "operational",
                "database": "operational"
            }
        }
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """Readiness check"""
    return {
        "success": True,
        "data": {
            "ready": True
        }
    }


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> Dict[str, Any]:
    """Liveness check"""
    return {
        "success": True,
        "data": {
            "alive": True
        }
    }


# ============================================
# CORE ROUTERS - ONLY ESSENTIAL MODULES
# ============================================

# Import ONLY core routers to save memory
from backend.services.auth.router import router as auth_router
from backend.services.dashboard.router import router as dashboard_router
from backend.services.masterdata.router import router as masterdata_router
from backend.services.customer.router import router as customer_router
from backend.services.loan import router as loan_router

# Register core routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(masterdata_router, prefix="/api/v1/masterdata", tags=["Master Data"])
app.include_router(customer_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(loan_router, prefix="/api/v1", tags=["Loans"])

logger.info("✅ Core routers registered: Auth, Dashboard, MasterData, Customers, Loans")
logger.info("💡 To add more modules, edit main_minimal.py or switch to main.py")

# ============================================
# APPLICATION READY
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_minimal:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.APP_DEBUG
    )
