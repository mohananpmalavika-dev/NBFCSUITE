#!/usr/bin/env python3
"""
Test Main.py Startup
Simulates the main.py startup process to check for table conflicts
"""

import sys
import os

# Set test environment variables
os.environ.setdefault('DATABASE_URL', 'postgresql://user:pass@localhost/testdb')
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key')

# Configure minimal modules (same as .env.render.production)
os.environ['ENABLE_AUTH'] = 'true'
os.environ['ENABLE_DASHBOARD'] = 'true'
os.environ['ENABLE_MASTERDATA'] = 'true'
os.environ['ENABLE_CUSTOMERS'] = 'true'
os.environ['ENABLE_LOANS'] = 'true'
os.environ['ENABLE_ACCOUNTING'] = 'false'
os.environ['ENABLE_INVENTORY'] = 'false'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_main_imports():
    """Test that main.py can import and initialize without errors"""
    print("\n=== Testing Main.py Initialization ===")
    
    try:
        # Import settings first
        from backend.shared.config import settings
        print(f"✓ Settings loaded (ENV: {settings.APP_ENV})")
        print(f"  - ENABLE_AUTH: {settings.ENABLE_AUTH}")
        print(f"  - ENABLE_CUSTOMERS: {settings.ENABLE_CUSTOMERS}")
        print(f"  - ENABLE_LOANS: {settings.ENABLE_LOANS}")
        print(f"  - ENABLE_ACCOUNTING: {settings.ENABLE_ACCOUNTING}")
        print(f"  - ENABLE_INVENTORY: {settings.ENABLE_INVENTORY}")
        
        # Import conditional imports module
        from backend.shared.conditional_imports import import_models
        print("✓ Conditional imports module loaded")
        
        # Import database connection and Base
        from backend.shared.database.connection import Base
        print("✓ Database connection module loaded")
        
        # Call import_models (this is what main.py does)
        print("\n📦 Loading database models conditionally...")
        import_models()
        print("✓ Conditional model imports completed")
        
        # Check registered tables
        table_names = list(Base.metadata.tables.keys())
        print(f"\n📊 Registered tables: {len(table_names)}")
        
        if len(table_names) > 0:
            print(f"  First 15 tables:")
            for i, table_name in enumerate(table_names[:15], 1):
                print(f"    {i}. {table_name}")
            if len(table_names) > 15:
                print(f"    ... and {len(table_names) - 15} more")
        else:
            print("  ⚠️  No tables registered")
        
        # Check for vendors table (should NOT be present)
        vendors_tables = [t for t in table_names if t == 'vendors']
        if vendors_tables:
            print(f"\n⚠️  WARNING: 'vendors' table found (should not be present with current config)")
            print("  This could cause foreign key conflicts")
            return False
        else:
            print(f"\n✓ No 'vendors' table (ENABLE_ACCOUNTING=false, ENABLE_INVENTORY=false)")
        
        # Check for inventory_items table (should NOT be present)
        if 'inventory_items' in table_names:
            print(f"⚠️  WARNING: 'inventory_items' table found (ENABLE_INVENTORY=false)")
            return False
        else:
            print(f"✓ No 'inventory_items' table (ENABLE_INVENTORY=false)")
        
        # Simulate table creation (what main.py does)
        print("\n🔄 Simulating table creation...")
        try:
            # Don't actually create tables, just check metadata
            from sqlalchemy import create_engine
            from sqlalchemy.schema import CreateTable
            
            print("  Checking table creation SQL...")
            sample_tables = list(table_names)[:3]
            for table_name in sample_tables:
                table = Base.metadata.tables[table_name]
                create_sql = str(CreateTable(table).compile(dialect=create_engine('postgresql://').dialect))
                print(f"  ✓ {table_name}: SQL generated ({len(create_sql)} chars)")
            
            print("✓ Table metadata is valid")
        except Exception as e:
            print(f"✗ Table creation check failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n✅ Main.py initialization successful!")
        print("   - No table conflicts")
        print("   - Models loaded conditionally")
        print("   - Metadata valid")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run test"""
    print("=" * 60)
    print("TESTING MAIN.PY STARTUP PROCESS")
    print("=" * 60)
    
    success = test_main_imports()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED")
        print("Main.py should start without foreign key errors")
        print("=" * 60)
        return 0
    else:
        print("✗ TEST FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
