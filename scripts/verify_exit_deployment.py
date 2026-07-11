#!/usr/bin/env python3
"""
Exit Management Deployment Verification Script
Comprehensive verification of Exit Management deployment
"""

import sys
import os
from pathlib import Path
import asyncio
import httpx
from datetime import datetime
from typing import Dict, List, Tuple
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from backend.shared.database.connection import get_db_engine

# ANSI color codes
class Colors:
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'


def print_header(message: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(message: str):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


class DeploymentVerifier:
    """Exit Management Deployment Verifier"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.checks_passed = 0
        self.checks_failed = 0
        self.checks_warning = 0
    
    async def verify_database_tables(self) -> bool:
        """Verify all database tables exist"""
        print_header("Database Tables Verification")
        
        required_tables = [
            'exit_resignations',
            'exit_clearances',
            'exit_settlements',
            'exit_settlement_components',
            'exit_documents'
        ]
        
        try:
            engine = get_db_engine()
            async with engine.begin() as conn:
                all_exist = True
                for table in required_tables:
                    result = await conn.execute(
                        text(f"""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = '{table}'
                            )
                        """)
                    )
                    exists = result.scalar()
                    
                    if exists:
                        # Check row count
                        count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.scalar()
                        print_success(f"Table '{table}' exists ({count} records)")
                        self.checks_passed += 1
                    else:
                        print_error(f"Table '{table}' not found")
                        all_exist = False
                        self.checks_failed += 1
                
                return all_exist
        except Exception as e:
            print_error(f"Database verification failed: {str(e)}")
            self.checks_failed += len(required_tables)
            return False
    
    async def verify_database_enums(self) -> bool:
        """Verify all enums exist"""
        print_header("Database Enums Verification")
        
        required_enums = [
            'resignation_type',
            'resignation_status',
            'clearance_status',
            'settlement_status',
            'settlement_component_type',
            'exit_document_type'
        ]
        
        try:
            engine = get_db_engine()
            async with engine.begin() as conn:
                all_exist = True
                for enum_name in required_enums:
                    result = await conn.execute(
                        text(f"""
                            SELECT EXISTS (
                                SELECT 1 FROM pg_type 
                                WHERE typname = '{enum_name}'
                            )
                        """)
                    )
                    exists = result.scalar()
                    
                    if exists:
                        # Get enum values
                        enum_values_result = await conn.execute(
                            text(f"""
                                SELECT enumlabel 
                                FROM pg_enum 
                                JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
                                WHERE pg_type.typname = '{enum_name}'
                            """)
                        )
                        values = [row[0] for row in enum_values_result.fetchall()]
                        print_success(f"Enum '{enum_name}' exists ({len(values)} values)")
                        self.checks_passed += 1
                    else:
                        print_error(f"Enum '{enum_name}' not found")
                        all_exist = False
                        self.checks_failed += 1
                
                return all_exist
        except Exception as e:
            print_error(f"Enum verification failed: {str(e)}")
            self.checks_failed += len(required_enums)
            return False
    
    async def verify_database_indexes(self) -> bool:
        """Verify critical indexes exist"""
        print_header("Database Indexes Verification")
        
        try:
            engine = get_db_engine()
            async with engine.begin() as conn:
                result = await conn.execute(
                    text("""
                        SELECT COUNT(*) 
                        FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND tablename LIKE 'exit_%'
                    """)
                )
                count = result.scalar()
                
                if count >= 20:  # We expect 20+ indexes
                    print_success(f"Found {count} indexes on Exit Management tables")
                    self.checks_passed += 1
                    return True
                else:
                    print_warning(f"Only {count} indexes found (expected 20+)")
                    self.checks_warning += 1
                    return True
        except Exception as e:
            print_error(f"Index verification failed: {str(e)}")
            self.checks_failed += 1
            return False
    
    async def verify_database_functions(self) -> bool:
        """Verify helper functions exist"""
        print_header("Database Functions Verification")
        
        required_functions = [
            'calculate_settlement_net_payable',
            'check_all_clearances_completed',
            'update_clearance_overdue_status'
        ]
        
        try:
            engine = get_db_engine()
            async with engine.begin() as conn:
                all_exist = True
                for func_name in required_functions:
                    result = await conn.execute(
                        text(f"""
                            SELECT EXISTS (
                                SELECT 1 FROM pg_proc 
                                WHERE proname = '{func_name}'
                            )
                        """)
                    )
                    exists = result.scalar()
                    
                    if exists:
                        print_success(f"Function '{func_name}' exists")
                        self.checks_passed += 1
                    else:
                        print_error(f"Function '{func_name}' not found")
                        all_exist = False
                        self.checks_failed += 1
                
                return all_exist
        except Exception as e:
            print_error(f"Function verification failed: {str(e)}")
            self.checks_failed += len(required_functions)
            return False
    
    async def verify_api_endpoints(self) -> bool:
        """Verify API endpoints are accessible"""
        print_header("API Endpoints Verification")
        
        endpoints_to_check = [
            ('/api/v1/hrms/exit/resignations', 'Resignations'),
            ('/api/v1/hrms/exit/clearances', 'Clearances'),
            ('/api/v1/hrms/exit/settlements', 'Settlements'),
            ('/api/v1/hrms/exit/documents', 'Documents'),
            ('/api/v1/hrms/exit/dashboard/stats', 'Dashboard')
        ]
        
        all_accessible = True
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint, name in endpoints_to_check:
                url = f"{self.api_url}{endpoint}"
                try:
                    response = await client.get(url)
                    
                    # 401 is acceptable (authentication required)
                    # 200 is ideal (accessible)
                    if response.status_code in [200, 401]:
                        print_success(f"{name} endpoint accessible [{response.status_code}]")
                        self.checks_passed += 1
                    else:
                        print_error(f"{name} endpoint returned {response.status_code}")
                        all_accessible = False
                        self.checks_failed += 1
                
                except httpx.ConnectError:
                    print_error(f"{name} endpoint not reachable (server not running?)")
                    all_accessible = False
                    self.checks_failed += 1
                except Exception as e:
                    print_error(f"{name} endpoint error: {str(e)}")
                    all_accessible = False
                    self.checks_failed += 1
        
        return all_accessible
    
    async def verify_api_documentation(self) -> bool:
        """Verify API documentation is accessible"""
        print_header("API Documentation Verification")
        
        docs_urls = [
            ('/docs', 'Swagger UI'),
            ('/redoc', 'ReDoc'),
            ('/openapi.json', 'OpenAPI Spec')
        ]
        
        all_accessible = True
        async with httpx.AsyncClient(timeout=10.0) as client:
            for endpoint, name in docs_urls:
                url = f"{self.api_url}{endpoint}"
                try:
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        print_success(f"{name} accessible")
                        self.checks_passed += 1
                    else:
                        print_warning(f"{name} returned {response.status_code}")
                        self.checks_warning += 1
                
                except Exception as e:
                    print_error(f"{name} error: {str(e)}")
                    all_accessible = False
                    self.checks_failed += 1
        
        return all_accessible
    
    async def verify_openapi_endpoints(self) -> bool:
        """Verify Exit Management endpoints in OpenAPI spec"""
        print_header("OpenAPI Specification Verification")
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_url}/openapi.json")
                
                if response.status_code != 200:
                    print_error("Could not fetch OpenAPI specification")
                    self.checks_failed += 1
                    return False
                
                spec = response.json()
                paths = spec.get('paths', {})
                
                exit_endpoints = [path for path in paths.keys() if '/hrms/exit' in path]
                
                if len(exit_endpoints) >= 30:  # We expect 33 endpoints
                    print_success(f"Found {len(exit_endpoints)} Exit Management endpoints in OpenAPI spec")
                    self.checks_passed += 1
                    
                    # List some endpoints
                    print_info("Sample endpoints:")
                    for endpoint in exit_endpoints[:5]:
                        print_info(f"  {endpoint}")
                    if len(exit_endpoints) > 5:
                        print_info(f"  ... and {len(exit_endpoints) - 5} more")
                    
                    return True
                else:
                    print_warning(f"Only {len(exit_endpoints)} endpoints found (expected 33)")
                    self.checks_warning += 1
                    return True
        
        except Exception as e:
            print_error(f"OpenAPI verification failed: {str(e)}")
            self.checks_failed += 1
            return False
    
    async def verify_backend_files(self) -> bool:
        """Verify backend files exist"""
        print_header("Backend Files Verification")
        
        required_files = [
            ('backend/shared/database/hrms_models.py', 'Database Models'),
            ('database/migrations/add_exit_management_tables.sql', 'Migration Script'),
            ('backend/services/hrms/schemas/exit_schemas.py', 'Pydantic Schemas'),
            ('backend/services/hrms/services/exit_service.py', 'Service Layer'),
            ('backend/services/hrms/routes/exit_routes.py', 'API Routes')
        ]
        
        all_exist = True
        base_path = Path(__file__).parent.parent
        
        for file_path, description in required_files:
            full_path = base_path / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print_success(f"{description} exists ({size:,} bytes)")
                self.checks_passed += 1
            else:
                print_error(f"{description} not found: {file_path}")
                all_exist = False
                self.checks_failed += 1
        
        return all_exist
    
    async def verify_frontend_files(self) -> bool:
        """Verify frontend files exist"""
        print_header("Frontend Files Verification")
        
        required_files = [
            ('frontend/apps/admin-portal/src/types/exit.types.ts', 'TypeScript Types'),
            ('frontend/apps/admin-portal/src/services/exit.service.ts', 'API Service'),
            ('frontend/apps/admin-portal/src/components/exit/ExitStatusBadge.tsx', 'Status Badge Component'),
            ('frontend/apps/admin-portal/src/components/exit/ResignationWorkflowStepper.tsx', 'Workflow Stepper'),
            ('frontend/apps/admin-portal/src/components/exit/ClearanceChecklist.tsx', 'Clearance Checklist'),
            ('frontend/apps/admin-portal/src/components/exit/SettlementBreakdown.tsx', 'Settlement Breakdown'),
            ('frontend/apps/admin-portal/src/components/exit/DocumentPreview.tsx', 'Document Preview')
        ]
        
        all_exist = True
        base_path = Path(__file__).parent.parent
        
        for file_path, description in required_files:
            full_path = base_path / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                print_success(f"{description} exists ({size:,} bytes)")
                self.checks_passed += 1
            else:
                print_error(f"{description} not found: {file_path}")
                all_exist = False
                self.checks_failed += 1
        
        return all_exist
    
    def print_summary(self):
        """Print verification summary"""
        print_header("Deployment Verification Summary")
        
        total_checks = self.checks_passed + self.checks_failed + self.checks_warning
        
        print(f"{Colors.BOLD}Total Checks: {total_checks}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Passed: {self.checks_passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed: {self.checks_failed}{Colors.ENDC}")
        print(f"{Colors.WARNING}Warnings: {self.checks_warning}{Colors.ENDC}")
        
        success_rate = (self.checks_passed / total_checks * 100) if total_checks > 0 else 0
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.ENDC}")
        
        if self.checks_failed == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Deployment verification passed!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Exit Management module is ready for production.{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Deployment verification failed!{Colors.ENDC}")
            print(f"{Colors.FAIL}Please fix the issues before deploying to production.{Colors.ENDC}")
        
        # Print deployment checklist
        print(f"\n{Colors.BOLD}Production Deployment Checklist:{Colors.ENDC}")
        checklist_items = [
            ("Database migration executed", self.checks_failed == 0),
            ("All API endpoints accessible", self.checks_failed == 0),
            ("Backend files in place", self.checks_failed == 0),
            ("Frontend files in place", self.checks_failed == 0),
            ("API documentation available", self.checks_warning == 0)
        ]
        
        for item, status in checklist_items:
            if status:
                print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {item}")
            else:
                print(f"  {Colors.FAIL}✗{Colors.ENDC} {item}")
    
    async def run_all_verifications(self):
        """Run all verification checks"""
        print_header("Exit Management Deployment Verification")
        print_info(f"API URL: {self.api_url}")
        print_info(f"Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Run all verifications
        await self.verify_database_tables()
        await self.verify_database_enums()
        await self.verify_database_indexes()
        await self.verify_database_functions()
        await self.verify_api_endpoints()
        await self.verify_api_documentation()
        await self.verify_openapi_endpoints()
        await self.verify_backend_files()
        await self.verify_frontend_files()
        
        # Print summary
        self.print_summary()
        
        # Return success status
        return self.checks_failed == 0


async def main():
    """Main entry point"""
    print("=" * 70)
    print("Exit Management Deployment Verification".center(70))
    print("=" * 70 + "\n")
    
    # Get API URL from environment
    api_url = os.getenv('API_URL', 'http://localhost:8000')
    
    # Create verifier and run
    verifier = DeploymentVerifier(api_url=api_url)
    success = await verifier.run_all_verifications()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Verification interrupted{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.FAIL}Error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
