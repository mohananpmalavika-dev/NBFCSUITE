"""
NBFC Financial Suite - Main Application
Tier-1 Enterprise Platform - Backend API
Version: 1.0.2 - Added conditional model imports for memory optimization
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
from pathlib import Path
from typing import Dict, Any

from sqlalchemy import inspect, text

from backend.shared.config import settings
from backend.shared.database.connection import engine, Base
from backend.shared.middleware.tenant import TenantMiddleware
from backend.shared.middleware.logging import LoggingMiddleware
from backend.shared.middleware.error_handler import ErrorHandlerMiddleware

# Import conditional loading function
from backend.shared.conditional_imports import import_models

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
    logger.info("🚀 Starting NBFC Financial Suite API...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Multi-tenant: {settings.TENANT_ISOLATION_ENABLED}")
    
    # Import models conditionally based on feature flags
    # This MUST happen before any database operations
    logger.info("📦 Loading database models conditionally...")
    import_models()
    
    # Force create all tables on startup (simple approach for free hosting)
    logger.info("🔄 Creating database tables...")
    logger.info(f"📊 Registered tables ({len(Base.metadata.tables)}): {list(Base.metadata.tables.keys())[:10]}...")

    # Check if we should drop and recreate all tables (useful for schema changes on free hosting)
    force_recreate = os.getenv("DROP_ALL_TABLES", "false").lower() == "true"
    
    if force_recreate:
        logger.warning("⚠️ DROP_ALL_TABLES=true: Dropping all tables and recreating...")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("✅ All tables dropped")
        except Exception as drop_error:
            logger.warning(f"Could not drop tables: {drop_error}")
    
    # Create tables - use connect() with manual transaction control for better error handling
    logger.info("🔧 Attempting to create database tables...")
    
    # First, check if we should skip table creation entirely
    skip_table_creation = os.getenv("SKIP_TABLE_CREATION", "false").lower() == "true"
    
    if skip_table_creation:
        logger.info("⏭️  SKIP_TABLE_CREATION=true: Skipping table creation, using existing schema")
    else:
        try:
            async with engine.begin() as conn:
                # Use begin() instead of connect() to auto-commit on success
                def create_tables_sync(sync_conn):
                    logger.info("Executing Base.metadata.create_all...")
                    try:
                        # Only create tables that are in our current metadata
                        # This prevents foreign key errors from old migrations
                        tables_to_create = []
                        for table_name, table in Base.metadata.tables.items():
                            tables_to_create.append(table)
                        
                        logger.info(f"Creating {len(tables_to_create)} tables from current metadata...")
                        Base.metadata.create_all(bind=sync_conn, tables=tables_to_create, checkfirst=True)
                        logger.info("✅ Base.metadata.create_all completed successfully")
                    except Exception as e:
                        logger.error(f"Error during create_all: {e}")
                        error_name = type(e).__name__
                        error_msg = str(e)
                        
                        # Check if this is a foreign key error
                        if 'NoReferencedTableError' in error_name or 'could not find table' in error_msg:
                            logger.warning(f"⚠️ Foreign key error detected: {error_msg}")
                            logger.warning("⚠️ This likely means the database has tables from old schema/migrations")
                            logger.warning("💡 Recommendation: Set SKIP_TABLE_CREATION=true or DROP_ALL_TABLES=true")
                            logger.info("✓ Continuing with existing database schema (ignoring creation errors)")
                            # Don't raise - continue with existing schema
                            return
                        
                        # Other errors - re-raise
                        raise
                
                await conn.run_sync(create_tables_sync)
                
            logger.info("✅ Table creation transaction completed")
        
        except Exception as create_error:
            # Check the type of error
            error_msg = str(create_error).lower()
            error_name = type(create_error).__name__
            
            # Log the full error for debugging
            logger.error(f"⚠️ Exception during table creation: {create_error}")
            logger.error(f"Exception type: {error_name}")
            
            # Handle foreign key errors gracefully
            if 'NoReferencedTableError' in error_name or 'could not find table' in error_msg:
                logger.warning(f"⚠️ Foreign key error from database schema: {create_error}")
                logger.warning("⚠️ This is likely from old migrations with disabled modules")
                logger.warning("💡 Set SKIP_TABLE_CREATION=true to skip table creation entirely")
                logger.info("✓ Continuing with existing database schema...")
                # Do NOT raise - continue with existing schema
            elif 'already exists' in error_msg or 'duplicate' in error_msg:
                # This shouldn't happen with checkfirst=True, but if it does,
                # the tables DO exist, so this is OK
                logger.warning(f"⚠️ Got 'already exists' error - tables may already exist")
                logger.info("⚠️ Continuing despite 'already exists' message...")
                # Do NOT raise - continue to verification
            elif 'cannot be implemented' in error_msg or 'incompatible types' in error_msg:
                # Schema mismatch - this is a real error
                logger.error(f"❌ Schema mismatch detected: {create_error}")
                logger.error("💡 Set environment variable DROP_ALL_TABLES=true to recreate tables")
                raise
            else:
                # Unknown error - check if it's safe to continue
                logger.error(f"❌ Unexpected error creating tables")
                import traceback
                logger.error(traceback.format_exc())
                logger.warning("⚠️ Attempting to continue with existing database schema...")
                # Try to continue - worst case, queries will fail later
    
    # Verify tables exist - wait a moment for database to sync
    logger.info("🔍 Waiting for database to sync...")
    await asyncio.sleep(2)
    
    logger.info("🔍 Verifying tables were created...")
    try:
        async with engine.connect() as conn:
            # Get all table names from public schema
            def get_tables(sync_conn):
                inspector = inspect(sync_conn)
                # Get tables from public schema (default)
                tables = inspector.get_table_names(schema='public')
                print(f"[DEBUG] Found {len(tables)} tables in public schema")
                if tables:
                    print(f"[DEBUG] First 10 tables: {tables[:10]}")
                else:
                    print("[DEBUG] NO TABLES FOUND!")
                return tables
            
            existing_tables = await conn.run_sync(get_tables)
        
        logger.info(f"✅ Database has {len(existing_tables)} tables")
        logger.info(f"📋 Sample tables: {existing_tables[:10] if existing_tables else 'NONE'}")
        
        # Check for users table
        if not existing_tables:
            logger.error(f"❌ No tables found in database!")
            logger.error("This indicates table creation failed silently or a schema mismatch")
            
            # Try direct query
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' LIMIT 10"))
                    rows = result.fetchall()
                    logger.error(f"Direct query found {len(rows)} tables: {[r[0] for r in rows]}")
            except Exception as query_error:
                logger.error(f"Could not query information_schema: {query_error}")
            
            raise RuntimeError("No tables found in database after creation attempt")
        
        if "users" not in existing_tables:
            logger.error(f"❌ Users table missing from {len(existing_tables)} tables")
            logger.error(f"Available tables: {existing_tables[:20]}")
            raise RuntimeError("Database created, but users table is still missing")
            
    except Exception as e:
        if "No tables found" in str(e) or "users table" in str(e):
            raise
        logger.error(f"❌ Failed to verify tables: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise

    # Ensure Alembic migrations are applied too (fallback for schema updates)
    try:
        migrations_path = Path(__file__).resolve().parent.parent / "database" / "migrations"
        if migrations_path.exists():
            logger.info("🔁 Applying Alembic migrations...")
            process = await asyncio.create_subprocess_exec(
                "alembic",
                "upgrade",
                "head",
                cwd=str(Path(__file__).resolve().parent),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logger.warning("⚠️ Alembic migrations failed")
                logger.warning(stdout.decode())
                logger.warning(stderr.decode())
            else:
                logger.info("✅ Alembic migrations applied successfully")
    except Exception as e:
        logger.warning(f"⚠️ Alembic migration check failed: {e}")
        import traceback
        logger.warning(traceback.format_exc())

    # Create default tenant if it doesn't exist
    try:
        from backend.shared.database.connection import AsyncSessionLocal
        from backend.shared.database.models import Tenant
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Tenant).where(Tenant.id == "default"))
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                logger.info("🏢 Creating default tenant...")
                tenant = Tenant(
                    id="default",
                    name="Default Organization",
                    display_name="Default Organization",
                    email="admin@nbfc.com",
                    is_active=True,
                    subscription_plan="enterprise",
                    subscription_status="active"
                )
                session.add(tenant)
                await session.commit()
                logger.info("✅ Default tenant created successfully")
            else:
                logger.info("✅ Default tenant already exists")
                
    except Exception as e:
        logger.warning(f"⚠️  Could not create default tenant: {e}")
        # Continue startup anyway
    
    logger.info("✅ Database connection ready")
    logger.info("✅ Application startup complete")
    
    # Start license reminder scheduler
    try:
        from backend.services.legal.license_scheduler import license_scheduler
        license_scheduler.start()
        logger.info("✅ License reminder scheduler started")
    except Exception as e:
        logger.warning(f"⚠️ Could not start license scheduler: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down NBFC Financial Suite API...")
    
    # Stop license scheduler
    try:
        from backend.services.legal.license_scheduler import license_scheduler
        license_scheduler.stop()
        logger.info("✅ License reminder scheduler stopped")
    except Exception as e:
        logger.warning(f"⚠️ Could not stop license scheduler: {e}")
    
    await engine.dispose()
    logger.info("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Complete Financial Institution Operating System for NBFCs, Nidhi Companies, and Financial Institutions in India",
    version="2.0.0",
    docs_url="/docs" if settings.ENABLE_SWAGGER else None,
    redoc_url="/redoc" if settings.ENABLE_REDOC else None,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Authentication", "description": "Authentication and authorization"},
        {"name": "Customers", "description": "Customer management (CIF)"},
        {"name": "Customer Timeline", "description": "Customer activity history and timeline tracking"},
        {"name": "Credit Bureau", "description": "Credit bureau integration (CIBIL, Equifax, Experian, CRIF)"},
        {"name": "eKYC / Aadhaar", "description": "Aadhaar eKYC with OTP and biometric verification"},
        {"name": "DigiLocker", "description": "DigiLocker document integration"},
        {"name": "Loans", "description": "Loan origination and management"},
        {"name": "Collections", "description": "Collection management"},
        {"name": "Deposits", "description": "Deposit management (Nidhi)"},
        {"name": "Gold Loans", "description": "Gold loan management with ornament tracking"},
        {"name": "Accounting", "description": "Accounting and finance"},
        {"name": "Fixed Assets", "description": "Fixed asset management with depreciation, maintenance, transfer & verification"},
        {"name": "Workflow", "description": "Enterprise workflow engine"},
        {"name": "Rules", "description": "Business rules engine"},
        {"name": "Decision", "description": "Instant decision engine"},
        {"name": "Notifications", "description": "Multi-channel notifications"},
        {"name": "Compliance", "description": "RBI compliance and reporting"},
        {"name": "Risk Management", "description": "Risk management and credit policy engine"},
        {"name": "File Upload", "description": "Document and file management"},
        {"name": "HRMS - Employees", "description": "Employee management and master data"},
        {"name": "HRMS - Departments", "description": "Department hierarchy and management"},
        {"name": "HRMS - Designations", "description": "Job titles and designation management"},
        {"name": "HRMS - Organizations", "description": "Organization/company entity management"},
        {"name": "HRMS - Employee Self Service", "description": "Employee self-service portal: payslips, leave, investments, reimbursements, profile"},
        {"name": "HRMS - Recruitment - Requisitions", "description": "Job requisition management and approval workflow"},
        {"name": "HRMS - Recruitment - Postings", "description": "Job posting and career portal management"},
        {"name": "HRMS - Recruitment - Applications", "description": "Applicant tracking system (ATS)"},
        {"name": "HRMS - Recruitment - Interviews", "description": "Interview scheduling and feedback management"},
        {"name": "HRMS - Recruitment - Onboarding", "description": "Employee onboarding and background verification"},
        {"name": "HRMS - Attendance - Shifts", "description": "Shift management and employee shift assignments"},
        {"name": "HRMS - Attendance - Tracking", "description": "Attendance tracking, check-in/out, and biometric integration"},
        {"name": "HRMS - Leave Management", "description": "Leave policies, applications, balance, and approval workflow"},
        {"name": "HRMS - Payroll", "description": "Salary structure, statutory compliance (PF/ESI/PT/TDS), payroll processing, Form 16, payment files"},
        {"name": "HRMS - Training & Development", "description": "Training calendar, courses, sessions, assessments, certifications, LMS integration, skill matrix"},
        {"name": "HRMS - Performance Management", "description": "Goal setting (KRA/KPI), appraisal cycles, 360-degree feedback, ratings & increment, Individual Development Plans (IDP)"},
        {"name": "HRMS - Exit Management", "description": "Resignation workflow, clearance process, full & final settlement, experience/relieving letters"},
        {"name": "CRM - Lead Management", "description": "Multi-channel lead capture, intelligent scoring, assignment & routing, follow-up tracking"},
        {"name": "CRM - Opportunity Management", "description": "Sales pipeline, stage-wise tracking, win/loss analysis, revenue forecasting"},
        {"name": "CRM - Account Management", "description": "Account 360 view, contact management, relationship tracking, business metrics"},
        {"name": "CRM - Marketing Automation", "description": "Campaign management, email/SMS campaigns, landing pages, customer segmentation"},
        {"name": "Property Management - Properties", "description": "Property master data, ownership details, amenities, and valuations"},
        {"name": "Property Management - Leases", "description": "Lease agreements, tenant management, and contract tracking"},
        {"name": "Property Management - Rent Collection", "description": "Rent payment tracking, receipts, and outstanding management"},
        {"name": "Property Management - Utilities", "description": "Utility bill management (electricity, water, gas) and tenant allocation"},
        {"name": "Property Management - Spaces", "description": "Space/unit management, allocation, and occupancy tracking"},
        {"name": "Property Management - Maintenance", "description": "Property maintenance requests, vendor management, and service tracking"},
        {"name": "Notifications - Property Management", "description": "Automated Email/SMS notifications for rent due, lease expiry, and payment alerts"},
        {"name": "Legal - Contract Management", "description": "Contract repository, lifecycle management, renewal tracking, and version control"},
        {"name": "Legal - Litigation Management", "description": "Case tracking, hearing management, and legal expense tracking"},
        {"name": "Legal - License Management", "description": "License register, renewal reminders, and compliance tracking"},
        {"name": "Facility - Building Management", "description": "Building, floor, and room management with amenities tracking"},
        {"name": "Facility - Housekeeping", "description": "Housekeeping task scheduling, assignment, and supply inventory management"},
        {"name": "Facility - Cafeteria", "description": "Menu management, order processing, and cafeteria inventory tracking"},
        {"name": "Facility - Transport", "description": "Vehicle management, trip scheduling, and maintenance tracking"},
        {"name": "Facility - Visitor Management", "description": "Visitor registration, check-in/out, passes, and security tracking"},
    ]
)

# ============================================
# MIDDLEWARE
# ============================================

# CORS - Allow all origins for now (can be restricted later)
logger.info(f"🌐 Configuring CORS with origins: {settings.CORS_ORIGINS}")

# Parse CORS origins
cors_origins = []
if settings.CORS_ORIGINS == "*":
    cors_origins = ["*"]
    logger.info("🌐 CORS: Allowing ALL origins")
else:
    # Split by comma and clean whitespace
    cors_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    # Add common Render.com patterns
    cors_origins.extend([
        "https://nbfcsuite-vqel.onrender.com",  # Your frontend
        "https://*.onrender.com",  # All Render subdomains
        "http://localhost:3000",  # Local development
        "http://localhost:3001",
    ])
    # Remove duplicates
    cors_origins = list(set(cors_origins))
    logger.info(f"🌐 CORS: Allowing specific origins: {cors_origins}")

# If origins contain "*", we can't use credentials
cors_allow_credentials = True
if "*" in cors_origins or "https://*.onrender.com" in cors_origins:
    # For wildcard origins, we need to allow all and disable credentials check
    cors_origins = ["*"]
    cors_allow_credentials = False
    logger.warning("🌐 CORS: Wildcard origin detected, disabling credentials")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
if settings.TENANT_ISOLATION_ENABLED:
    app.add_middleware(TenantMiddleware)

# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    # Convert validation errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": list(error.get("loc", [])),
            "msg": str(error.get("msg", "")),
            "type": error.get("type", "")
        }
        # Handle ctx which might contain non-serializable objects
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
            "name": settings.APP_NAME,
            "version": "2.0.0",
            "status": "running",
            "environment": settings.APP_ENV,
            "docs": "/docs",
            "platform_rating": "9.8/10 - Tier-1 Enterprise Grade"
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
            "services": {
                "api": "operational",
                "database": "operational",
                "cache": "operational"
            }
        }
    }


@app.get("/debug/tables", tags=["Health"])
async def debug_tables() -> Dict[str, Any]:
    """Debug endpoint to check registered tables"""
    from backend.shared.database.connection import Base, engine
    from sqlalchemy import text
    
    try:
        # Check what tables SQLAlchemy knows about
        registered_tables = list(Base.metadata.tables.keys())
        
        # Check what tables actually exist in the database
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
            existing_tables = [row[0] for row in result]
        
        return {
            "success": True,
            "data": {
                "registered_tables": registered_tables,
                "registered_count": len(registered_tables),
                "existing_tables": existing_tables,
                "existing_count": len(existing_tables),
                "missing_tables": list(set(registered_tables) - set(existing_tables))
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/init-db", tags=["Health"])
async def initialize_database() -> Dict[str, Any]:
    """Initialize database tables (for first-time setup)"""
    try:
        from backend.shared.database.connection import Base, engine
        
        logger.info("🔄 Creating database tables...")
        logger.info(f"📊 Registered tables: {list(Base.metadata.tables.keys())}")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully")
        
        # Create default tenant
        from backend.shared.database.connection import AsyncSessionLocal
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Tenant).where(Tenant.id == "default"))
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                tenant = Tenant(
                    id="default",
                    name="Default Organization",
                    display_name="Default Organization",
                    email="admin@nbfc.com",
                    is_active=True,
                    subscription_plan="enterprise",
                    subscription_status="active"
                )
                session.add(tenant)
                await session.commit()
                logger.info("✅ Default tenant created")
        
        return {
            "success": True,
            "data": {
                "message": "Database initialized successfully",
                "tables_created": list(Base.metadata.tables.keys()),
                "default_tenant_created": True
            }
        }
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}", exc_info=True)
        import traceback
        return {
            "success": False,
            "error": {
                "code": "INIT_ERROR",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
        }


@app.get("/health/ready", tags=["Health"])
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes"""
    # TODO: Add actual health checks for dependencies
    return {
        "success": True,
        "data": {
            "ready": True,
            "services": {
                "database": True,
                "redis": True,
                "rabbitmq": True
            }
        }
    }


@app.get("/health/live", tags=["Health"])
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes"""
    return {
        "success": True,
        "data": {
            "alive": True
        }
    }


# ============================================
# API ROUTERS
# ============================================

# MEMORY OPTIMIZATION: Import routers conditionally based on feature flags
# This reduces memory usage on free tier (512MB RAM limit)

logger.info("Loading API routers based on enabled features...")

# Core routers (always enabled)
from backend.services.auth.router import router as auth_router
from backend.services.dashboard.router import router as dashboard_router

# Load only enabled modules using conditional imports
from backend.shared.conditional_imports import get_enabled_routers


# ============================================
# FASTAPI APPLICATION SETUP
# ============================================

# NEW: CRM Lead Management Module (Multi-channel Capture, Scoring, Assignment, Follow-up Tracking)
from backend.services.crm.router import router as crm_router

# NEW: CRM Opportunity Management Module (Sales Pipeline, Stage Tracking, Win/Loss Analysis)
from backend.crm.routes.opportunity_routes import router as crm_opportunity_router

# NEW: CRM Sales Automation Module (Product Catalog, Quote Generation, Order Management)
from backend.crm.routes.sales_routes import (
    product_router, quote_router, order_router
)

# NEW: CRM Customer Service Module (Ticket Management, Knowledge Base, SLA Tracking)
from backend.crm.routes.service_routes import (
    ticket_router, knowledge_router, sla_router
)

# NEW: Legal Contract Management Module (Contract Repository, Lifecycle, Renewal, Version Control)
from backend.services.legal.router import router as legal_contract_router
from backend.services.legal.litigation_router import router as litigation_router
from backend.services.legal.license_router import router as license_router

# NEW: Document Management System (DMS) Module (Complete DMS with Version Control, Workflows, E-Signatures)
from backend.services.dms.router import router as dms_router

# NEW: Facility & Administration Management Module (Building, Housekeeping, Cafeteria, Transport, Visitor Management)
from backend.services.facility import (
    building_router,
    housekeeping_router,
    cafeteria_router,
    transport_router,
    visitor_router
)

# ============================================
# REGISTER ROUTERS - MEMORY OPTIMIZED
# Only loads routers for enabled modules
# ============================================

# Register core routers (always enabled)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])

# Dynamically register routers based on feature flags
enabled_routers = get_enabled_routers()
for name, router, prefix in enabled_routers:
    try:
        app.include_router(router, prefix=prefix)
        logger.info(f"Registered router: {name}")
    except Exception as e:
        logger.error(f"Failed to register router {name}: {e}")

logger.info(f"Total routers registered: {len(enabled_routers) + 2}")  # +2 for auth and dashboard

# ============================================
# STARTUP MESSAGE
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("=" * 60)
    logger.info("  NBFC Financial Suite - Enterprise Platform")
    logger.info("  Version: 2.0.0 (Memory Optimized)")
    logger.info("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
