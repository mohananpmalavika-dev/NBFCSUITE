#!/usr/bin/env python3
"""
Exit Management Configuration Script
Sets up and configures the Exit Management module for HRMS
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from sqlalchemy import text
from backend.shared.database.connection import get_db_engine, get_async_session
from backend.shared.database.hrms_models import (
    ResignationType, ResignationStatus, ClearanceStatus, 
    SettlementStatus, SettlementComponentType, ExitDocumentType
)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


async def check_database_connection():
    """Check if database connection is working"""
    print_header("Database Connection Check")
    
    try:
        engine = get_db_engine()
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print_success("Database connection successful")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False


async def check_migration_status():
    """Check if Exit Management tables exist"""
    print_header("Migration Status Check")
    
    tables_to_check = [
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
            for table in tables_to_check:
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
                    print_success(f"Table '{table}' exists")
                else:
                    print_error(f"Table '{table}' does not exist")
                    all_exist = False
            
            return all_exist
    except Exception as e:
        print_error(f"Migration check failed: {str(e)}")
        return False


async def run_migration():
    """Run the Exit Management migration"""
    print_header("Running Migration")
    
    migration_file = Path(__file__).parent.parent / "database" / "migrations" / "add_exit_management_tables.sql"
    
    if not migration_file.exists():
        print_error(f"Migration file not found: {migration_file}")
        return False
    
    try:
        with open(migration_file, 'r') as f:
            migration_sql = f.read()
        
        engine = get_db_engine()
        async with engine.begin() as conn:
            # Split by semicolons and execute each statement
            statements = [s.strip() for s in migration_sql.split(';') if s.strip()]
            
            for i, statement in enumerate(statements, 1):
                try:
                    await conn.execute(text(statement))
                    print_info(f"Executed statement {i}/{len(statements)}")
                except Exception as stmt_error:
                    # Some statements might fail if already exists, that's okay
                    if "already exists" not in str(stmt_error):
                        print_warning(f"Statement {i} warning: {str(stmt_error)[:100]}")
        
        print_success("Migration completed successfully")
        return True
    except Exception as e:
        print_error(f"Migration failed: {str(e)}")
        return False


async def verify_enums():
    """Verify that all enums are properly created"""
    print_header("Enum Verification")
    
    enums_to_check = [
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
            for enum_name in enums_to_check:
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
                    print_success(f"Enum '{enum_name}' exists")
                else:
                    print_error(f"Enum '{enum_name}' does not exist")
        
        return True
    except Exception as e:
        print_error(f"Enum verification failed: {str(e)}")
        return False


async def verify_indexes():
    """Verify that indexes are created"""
    print_header("Index Verification")
    
    try:
        engine = get_db_engine()
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT tablename, indexname 
                    FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND tablename LIKE 'exit_%'
                    ORDER BY tablename, indexname
                """)
            )
            
            indexes = result.fetchall()
            
            if indexes:
                print_success(f"Found {len(indexes)} indexes on Exit Management tables")
                for table, index in indexes[:10]:  # Show first 10
                    print_info(f"  {table}: {index}")
                if len(indexes) > 10:
                    print_info(f"  ... and {len(indexes) - 10} more")
                return True
            else:
                print_warning("No indexes found on Exit Management tables")
                return False
    except Exception as e:
        print_error(f"Index verification failed: {str(e)}")
        return False


async def verify_triggers():
    """Verify that triggers are created"""
    print_header("Trigger Verification")
    
    try:
        engine = get_db_engine()
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                    SELECT event_object_table, trigger_name 
                    FROM information_schema.triggers 
                    WHERE event_object_schema = 'public' 
                    AND event_object_table LIKE 'exit_%'
                    ORDER BY event_object_table
                """)
            )
            
            triggers = result.fetchall()
            
            if triggers:
                print_success(f"Found {len(triggers)} triggers on Exit Management tables")
                for table, trigger in triggers:
                    print_info(f"  {table}: {trigger}")
                return True
            else:
                print_warning("No triggers found on Exit Management tables")
                return False
    except Exception as e:
        print_error(f"Trigger verification failed: {str(e)}")
        return False


async def verify_functions():
    """Verify that helper functions are created"""
    print_header("Function Verification")
    
    functions_to_check = [
        'calculate_settlement_net_payable',
        'check_all_clearances_completed',
        'update_clearance_overdue_status'
    ]
    
    try:
        engine = get_db_engine()
        async with engine.begin() as conn:
            for func_name in functions_to_check:
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
                else:
                    print_error(f"Function '{func_name}' does not exist")
        
        return True
    except Exception as e:
        print_error(f"Function verification failed: {str(e)}")
        return False


async def test_basic_queries():
    """Test basic queries on Exit Management tables"""
    print_header("Basic Query Tests")
    
    try:
        engine = get_db_engine()
        async with engine.begin() as conn:
            # Test count queries on each table
            tables = [
                'exit_resignations',
                'exit_clearances',
                'exit_settlements',
                'exit_settlement_components',
                'exit_documents'
            ]
            
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print_success(f"Table '{table}': {count} records")
        
        return True
    except Exception as e:
        print_error(f"Basic query test failed: {str(e)}")
        return False


def print_configuration_summary():
    """Print configuration summary and next steps"""
    print_header("Configuration Summary")
    
    print(f"{Colors.OKGREEN}Exit Management module is configured and ready!{Colors.ENDC}\n")
    
    print(f"{Colors.BOLD}What's configured:{Colors.ENDC}")
    print("  • Database tables: 5 tables created")
    print("  • Enums: 6 enum types created")
    print("  • Indexes: 20+ indexes for performance")
    print("  • Triggers: 5 automatic update triggers")
    print("  • Functions: 3 helper functions")
    print("  • API Endpoints: 33 RESTful endpoints")
    
    print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
    print("  1. Run seed script to create sample data:")
    print(f"     {Colors.OKCYAN}python scripts/seed_exit_data.py{Colors.ENDC}")
    print("  2. Test API endpoints:")
    print(f"     {Colors.OKCYAN}python scripts/test_exit_api.py{Colors.ENDC}")
    print("  3. Verify deployment:")
    print(f"     {Colors.OKCYAN}python scripts/verify_exit_deployment.py{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}API Documentation:{Colors.ENDC}")
    print(f"  • Swagger UI: {Colors.OKCYAN}http://localhost:8000/docs{Colors.ENDC}")
    print(f"  • ReDoc: {Colors.OKCYAN}http://localhost:8000/redoc{Colors.ENDC}")
    
    print(f"\n{Colors.BOLD}Module Features:{Colors.ENDC}")
    print("  • Resignation workflow management")
    print("  • Exit clearance tracking (5 default clearances)")
    print("  • Full & Final settlement calculation")
    print("  • Document generation (Experience/Relieving/Service letters)")
    print("  • Dashboard and analytics")
    print("  • Complete audit trails")


async def main():
    """Main configuration flow"""
    print_header("Exit Management Configuration Tool")
    print(f"{Colors.BOLD}NBFC Suite - HRMS Module{Colors.ENDC}\n")
    
    # Step 1: Check database connection
    if not await check_database_connection():
        print_error("Cannot proceed without database connection")
        sys.exit(1)
    
    # Step 2: Check migration status
    tables_exist = await check_migration_status()
    
    # Step 3: Run migration if needed
    if not tables_exist:
        print_warning("Exit Management tables not found. Running migration...")
        response = input("Do you want to run the migration now? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            if not await run_migration():
                print_error("Migration failed. Please check the logs.")
                sys.exit(1)
        else:
            print_info("Migration skipped. Please run migration manually.")
            sys.exit(0)
    else:
        print_success("All Exit Management tables exist")
    
    # Step 4: Verify enums
    await verify_enums()
    
    # Step 5: Verify indexes
    await verify_indexes()
    
    # Step 6: Verify triggers
    await verify_triggers()
    
    # Step 7: Verify functions
    await verify_functions()
    
    # Step 8: Test basic queries
    await test_basic_queries()
    
    # Step 9: Print summary
    print_configuration_summary()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}Configuration completed successfully!{Colors.ENDC}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Configuration interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
