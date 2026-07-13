"""
NBFC Financial Suite - HRMS Service
Microservice Architecture - Human Resource Management Module

This service handles:
- Employee Management
- Department & Designation Management
- Attendance & Leave Management
- Payroll Processing
- Recruitment & Onboarding
- Performance Management
- Training & Development

Memory Footprint: ~200MB
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


def import_hrms_models():
    """Import only HRMS service models"""
    logger.info("📦 Loading HRMS Service models...")
    
    # 1. Core models (REQUIRED for auth)
    from backend.shared.database.models import (
        Tenant, User, Role, UserRole, Permission, RolePermission
    )
    
    # 2. HRMS Core models
    from backend.shared.database.hrms_models import (
        HRMSOrganization, Department, Designation, 
        Employee, ReportingHierarchy
    )
    
    # 3. HRMS Loan models
    from backend.shared.database.hrms_loan_models import (
        LoanPolicy, EmployeeLoan, LoanEMISchedule, 
        LoanTransaction, LoanType, LoanStatus, 
        RepaymentFrequency, EMIStatus, TransactionType
    )
    
    # 4. Recruitment models (if enabled)
    if settings.ENABLE_RECRUITMENT:
        from backend.shared.database.recruitment_models import (
            JobRequisition, JobPosting, JobApplication, Interview,
            Onboarding, BackgroundVerification
        )
    
    # 5. Attendance models (if enabled)
    if settings.ENABLE_ATTENDANCE:
        from backend.shared.database.attendance_models import (
            Shift, EmployeeShift, Attendance, BiometricLog, AttendanceRegularization,
            LeavePolicyMaster, EmployeeLeaveBalance, LeaveApplication, LeaveEncashment
        )
    
    # 6. Payroll models (if enabled)
    if settings.ENABLE_PAYROLL:
        from backend.shared.database.payroll_models import (
            SalaryComponent, SalaryStructure, SalaryStructureComponent, EmployeeSalary,
            EmployeeSalaryComponent, PayrollRun, Payslip, PayslipComponent,
            StatutoryCompliance, Form16, PaymentFile
        )
    
    # 7. Training models (if enabled)
    if settings.ENABLE_TRAINING:
        from backend.shared.database.training_models import (
            TrainingCourse, TrainingSession, TrainingParticipant,
            TrainingAssessment, AssessmentResult, TrainingCertification,
            Skill, EmployeeSkill
        )
    
    logger.info("✅ HRMS Service models loaded")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 Starting NBFC HRMS Service...")
    logger.info(f"Service: HRMS (Employees, Payroll, Attendance, Recruitment)")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database: Shared PostgreSQL")
    
    # Import models
    import_hrms_models()
    
    # Skip table creation (tables are managed centrally)
    skip_table_creation = os.getenv("SKIP_TABLE_CREATION", "true").lower() == "true"
    
    if skip_table_creation:
        logger.info("⏭️  SKIP_TABLE_CREATION=true: Using existing database schema")
    else:
        logger.info("🔧 Creating tables for HRMS service...")
        async with engine.begin() as conn:
            def create_tables_sync(sync_conn):
                Base.metadata.create_all(bind=sync_conn, checkfirst=True)
            await conn.run_sync(create_tables_sync)
        logger.info("✅ Tables created")
    
    logger.info("✅ HRMS Service startup complete")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HRMS Service...")
    await engine.dispose()
    logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="NBFC Financial Suite - HRMS Service",
    description="Human Resource Management microservice: Employees, Payroll, Attendance, Recruitment",
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
            "service": "NBFC HRMS Service",
            "version": "2.0.0-microservices",
            "status": "running",
            "modules": ["Employees", "Attendance", "Payroll", "Recruitment", "Performance", "Training"],
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
            "service": "hrms"
        }
    }


# Load routers dynamically
def load_hrms_routers():
    """Load only HRMS service routers"""
    logger.info("📍 Loading HRMS service routers...")
    
    # Core HRMS
    from backend.services.hrms import (
        employee_router, 
        department_router, 
        designation_router,
        ess_router
    )
    app.include_router(employee_router, prefix="/api/hrms", tags=["HRMS - Employees"])
    app.include_router(department_router, prefix="/api/hrms", tags=["HRMS - Departments"])
    app.include_router(designation_router, prefix="/api/hrms", tags=["HRMS - Designations"])
    app.include_router(ess_router, prefix="/api/hrms/ess", tags=["HRMS - Employee Self Service"])
    
    # Recruitment (if enabled)
    if settings.ENABLE_RECRUITMENT:
        logger.info("Loading Recruitment routers...")
        from backend.services.hrms.routes import exit_routes, performance_routes
        # Add recruitment routers when available
    
    # Attendance (if enabled)
    if settings.ENABLE_ATTENDANCE:
        logger.info("Loading Attendance & Leave routers...")
        # Add attendance routers when available
    
    # Payroll (if enabled)
    if settings.ENABLE_PAYROLL:
        logger.info("Loading Payroll routers...")
        # Add payroll routers when available
    
    # Training (if enabled)
    if settings.ENABLE_TRAINING:
        logger.info("Loading Training routers...")
        # Add training routers when available
    
    logger.info("✅ HRMS service routers loaded")


# Load routers
load_hrms_routers()

logger.info("✅ HRMS Service initialized and ready")
