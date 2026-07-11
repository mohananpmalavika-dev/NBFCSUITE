#!/usr/bin/env python3
"""
Performance Management Deployment Verification Script

This script verifies that all Performance Management components are
properly deployed and functional.

Usage:
    python verify_performance_deployment.py
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from typing import List, Dict, Any
import importlib.util


class DeploymentVerifier:
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []
        
    def log_pass(self, check_name: str, message: str = ""):
        """Log a passed check"""
        self.checks_passed.append({"name": check_name, "message": message})
        print(f"✓ {check_name}")
        if message:
            print(f"  → {message}")
            
    def log_fail(self, check_name: str, message: str = ""):
        """Log a failed check"""
        self.checks_failed.append({"name": check_name, "message": message})
        print(f"✗ {check_name}")
        if message:
            print(f"  → {message}")
            
    def log_warning(self, message: str):
        """Log a warning"""
        self.warnings.append(message)
        print(f"⚠ WARNING: {message}")
        
    def verify_database_tables(self, db_url: str):
        """Verify all database tables exist"""
        print("\n=== Verifying Database Tables ===")
        
        expected_tables = [
            'performance_appraisal_cycles',
            'performance_goals',
            'performance_employee_appraisals',
            'performance_feedback_requests',
            'performance_feedback_responses',
            'performance_increments',
            'performance_idps',
            'performance_development_activities'
        ]
        
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                # Get all tables
                result = conn.execute(text("""
                    SELECT tablename 
                    FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND tablename LIKE 'performance_%'
                """))
                
                existing_tables = [row[0] for row in result]
                
                # Check each expected table
                for table in expected_tables:
                    if table in existing_tables:
                        # Get row count
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.scalar()
                        self.log_pass(
                            f"Table: {table}",
                            f"{count} rows"
                        )
                    else:
                        self.log_fail(
                            f"Table: {table}",
                            "Table does not exist"
                        )
                        
                # Check for extra tables
                extra_tables = [t for t in existing_tables if t not in expected_tables]
                if extra_tables:
                    self.log_warning(f"Extra tables found: {', '.join(extra_tables)}")
                    
        except Exception as e:
            self.log_fail("Database Connection", str(e))
            
    def verify_database_enums(self, db_url: str):
        """Verify all database enums exist"""
        print("\n=== Verifying Database Enums ===")
        
        expected_enums = [
            'goaltype',
            'goalstatus',
            'appraisalcyclestatus',
            'appraisalstatus',
            'ratingscale',
            'feedbacktype',
            'incrementtype',
            'idpstatus',
            'developmentactivitytype',
            'developmentactivitystatus',
            'feedbackstatus'
        ]
        
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT typname 
                    FROM pg_type 
                    WHERE typtype = 'e'
                    AND typname IN :enum_list
                """), {"enum_list": tuple(expected_enums)})
                
                existing_enums = [row[0] for row in result]
                
                for enum in expected_enums:
                    if enum in existing_enums:
                        self.log_pass(f"Enum: {enum}")
                    else:
                        self.log_fail(f"Enum: {enum}", "Enum does not exist")
                        
        except Exception as e:
            self.log_fail("Enum Verification", str(e))
            
    def verify_database_indexes(self, db_url: str):
        """Verify important indexes exist"""
        print("\n=== Verifying Database Indexes ===")
        
        important_indexes = [
            'idx_perf_goals_appraisal',
            'idx_perf_goals_status',
            'idx_perf_appraisals_cycle',
            'idx_perf_appraisals_employee',
            'idx_perf_feedback_appraisal',
            'idx_perf_increments_appraisal'
        ]
        
        try:
            engine = create_engine(db_url)
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE schemaname = 'public'
                    AND indexname LIKE 'idx_perf%'
                """))
                
                existing_indexes = [row[0] for row in result]
                
                for index in important_indexes:
                    if index in existing_indexes:
                        self.log_pass(f"Index: {index}")
                    else:
                        self.log_warning(f"Index missing: {index}")
                        
                print(f"  → Total performance indexes: {len(existing_indexes)}")
                
        except Exception as e:
            self.log_fail("Index Verification", str(e))
            
    def verify_backend_files(self):
        """Verify backend files exist"""
        print("\n=== Verifying Backend Files ===")
        
        backend_files = [
            'backend/shared/database/hrms_models.py',
            'backend/services/hrms/schemas/performance_schemas.py',
            'backend/services/hrms/services/performance_service.py',
            'backend/services/hrms/routes/performance_routes.py'
        ]
        
        for file_path in backend_files:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                self.log_pass(
                    f"Backend file: {file_path}",
                    f"{size:,} bytes"
                )
            else:
                self.log_fail(f"Backend file: {file_path}", "File not found")
                
    def verify_backend_models(self):
        """Verify backend models are importable"""
        print("\n=== Verifying Backend Models ===")
        
        models_to_check = [
            'AppraisalCycle',
            'PerformanceGoal',
            'EmployeeAppraisal',
            'FeedbackRequest',
            'FeedbackResponse',
            'PerformanceIncrement',
            'IndividualDevelopmentPlan',
            'DevelopmentActivity'
        ]
        
        try:
            # Try to import the models module
            models_path = Path('backend/shared/database/hrms_models.py')
            if models_path.exists():
                spec = importlib.util.spec_from_file_location("hrms_models", models_path)
                if spec and spec.loader:
                    models_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(models_module)
                    
                    for model_name in models_to_check:
                        if hasattr(models_module, model_name):
                            self.log_pass(f"Model: {model_name}")
                        else:
                            self.log_fail(f"Model: {model_name}", "Model not found in module")
                else:
                    self.log_fail("Backend Models", "Could not load module spec")
            else:
                self.log_fail("Backend Models", "hrms_models.py not found")
        except Exception as e:
            self.log_fail("Backend Models Import", str(e))
            
    def verify_frontend_files(self):
        """Verify frontend files exist"""
        print("\n=== Verifying Frontend Files ===")
        
        frontend_files = [
            'frontend/apps/admin-portal/src/types/performance.types.ts',
            'frontend/apps/admin-portal/src/services/performance.service.ts',
            'frontend/apps/admin-portal/src/components/performance/RatingScaleSelector.tsx',
            'frontend/apps/admin-portal/src/components/performance/GoalProgressTracker.tsx',
            'frontend/apps/admin-portal/src/components/performance/StatusBadge.tsx',
            'frontend/apps/admin-portal/src/pages/performance/dashboard/PerformanceDashboard.tsx',
            'frontend/apps/admin-portal/src/pages/performance/cycles/AppraisalCycleList.tsx',
            'frontend/apps/admin-portal/src/pages/performance/goals/GoalsList.tsx',
            'frontend/apps/admin-portal/src/pages/performance/appraisals/SelfAssessmentForm.tsx',
            'frontend/apps/admin-portal/src/pages/performance/appraisals/ManagerReviewForm.tsx',
            'frontend/apps/admin-portal/src/pages/performance/PerformanceManagementRoutes.tsx'
        ]
        
        for file_path in frontend_files:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                self.log_pass(
                    f"Frontend file: {path.name}",
                    f"{size:,} bytes"
                )
            else:
                self.log_fail(f"Frontend file: {file_path}", "File not found")
                
    def verify_scripts(self):
        """Verify configuration scripts exist"""
        print("\n=== Verifying Configuration Scripts ===")
        
        scripts = [
            'scripts/configure_first_appraisal_cycle.py',
            'scripts/seed_performance_data.py',
            'scripts/test_performance_api.py',
            'scripts/verify_performance_deployment.py'
        ]
        
        for script_path in scripts:
            path = Path(script_path)
            if path.exists():
                # Check if executable
                is_executable = os.access(path, os.X_OK)
                self.log_pass(
                    f"Script: {path.name}",
                    "Executable" if is_executable else "Not executable (run with python)"
                )
            else:
                self.log_fail(f"Script: {script_path}", "File not found")
                
    def verify_documentation(self):
        """Verify documentation exists"""
        print("\n=== Verifying Documentation ===")
        
        docs = [
            'docs/HRMS_PERFORMANCE_MANAGEMENT_COMPLETE.md',
            'docs/PERFORMANCE_MANAGEMENT_IMPLEMENTATION_SUMMARY.md',
            'docs/PERFORMANCE_MANAGEMENT_UI_SPECIFICATION.md',
            'docs/PERFORMANCE_MANAGEMENT_SETUP_GUIDE.md',
            'docs/PERFORMANCE_MANAGEMENT_QUICK_REFERENCE.md',
            'docs/PERFORMANCE_MANAGEMENT_FINAL_SUMMARY.md',
            'docs/PERFORMANCE_MANAGEMENT_DEPLOYMENT_CHECKLIST.md',
            'docs/PERFORMANCE_MANAGEMENT_MASTER_INDEX.md'
        ]
        
        for doc_path in docs:
            path = Path(doc_path)
            if path.exists():
                # Count lines
                with open(path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                self.log_pass(
                    f"Documentation: {path.name}",
                    f"{lines} lines"
                )
            else:
                self.log_fail(f"Documentation: {doc_path}", "File not found")
                
    def verify_migration_script(self):
        """Verify database migration script exists"""
        print("\n=== Verifying Migration Script ===")
        
        migration_path = Path('database/migrations/add_performance_management_tables.sql')
        
        if migration_path.exists():
            with open(migration_path, 'r') as f:
                content = f.read()
                
            # Check for important SQL statements
            checks = {
                'CREATE TABLE': content.count('CREATE TABLE'),
                'CREATE TYPE': content.count('CREATE TYPE'),
                'CREATE INDEX': content.count('CREATE INDEX'),
                'CREATE TRIGGER': content.count('CREATE TRIGGER')
            }
            
            self.log_pass("Migration script exists", f"{migration_path.stat().st_size:,} bytes")
            
            for check_name, count in checks.items():
                if count > 0:
                    print(f"  → {check_name}: {count}")
                else:
                    self.log_warning(f"No {check_name} statements found")
        else:
            self.log_fail("Migration script", "File not found")
            
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 60)
        print("DEPLOYMENT VERIFICATION SUMMARY")
        print("=" * 60)
        
        total = len(self.checks_passed) + len(self.checks_failed)
        passed = len(self.checks_passed)
        failed = len(self.checks_failed)
        warnings = len(self.warnings)
        
        print(f"Total Checks: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        print(f"Warnings: {warnings} ⚠")
        
        if total > 0:
            print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if warnings > 0:
            print(f"\n⚠ WARNINGS ({warnings}):")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        if failed > 0:
            print(f"\n❌ FAILED CHECKS ({failed}):")
            for check in self.checks_failed:
                print(f"  - {check['name']}")
                if check['message']:
                    print(f"    {check['message']}")
        else:
            print("\n✅ ALL CHECKS PASSED!")
            
        print("\n" + "=" * 60)
        
        # Deployment status
        if failed == 0:
            print("STATUS: ✅ READY FOR PRODUCTION")
            return 0
        elif failed <= 5:
            print("STATUS: ⚠ MOSTLY READY (Minor issues to fix)")
            return 1
        else:
            print("STATUS: ❌ NOT READY (Multiple issues found)")
            return 2


def main():
    print("=" * 60)
    print("PERFORMANCE MANAGEMENT DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    verifier = DeploymentVerifier()
    
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost/nbfc_suite')
    
    print(f"\nDatabase URL: {db_url}")
    print("Note: Set DATABASE_URL environment variable if different\n")
    
    # Run all verifications
    verifier.verify_backend_files()
    verifier.verify_backend_models()
    verifier.verify_frontend_files()
    verifier.verify_scripts()
    verifier.verify_documentation()
    verifier.verify_migration_script()
    
    # Database checks (may fail if not deployed yet)
    try:
        verifier.verify_database_tables(db_url)
        verifier.verify_database_enums(db_url)
        verifier.verify_database_indexes(db_url)
    except Exception as e:
        print(f"\n⚠ Could not verify database: {e}")
        print("  → Database checks skipped (may not be deployed yet)")
    
    # Print summary and return exit code
    exit_code = verifier.print_summary()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
