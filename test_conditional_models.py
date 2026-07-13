#!/usr/bin/env python3
"""
Test Conditional Model Imports
Verifies that models are only imported when their feature flags are enabled
and that there are no table name conflicts
"""

import sys
import os

# Set test environment variables
os.environ.setdefault('DATABASE_URL', 'postgresql://user:pass@localhost/testdb')
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key')

# Configure minimal modules for test
os.environ['ENABLE_AUTH'] = 'true'
os.environ['ENABLE_DASHBOARD'] = 'true'
os.environ['ENABLE_MASTERDATA'] = 'true'
os.environ['ENABLE_CUSTOMERS'] = 'true'
os.environ['ENABLE_LOANS'] = 'true'

# Disable problematic modules
os.environ['ENABLE_ACCOUNTING'] = 'false'
os.environ['ENABLE_INVENTORY'] = 'false'
os.environ['ENABLE_HRMS'] = 'false'
os.environ['ENABLE_CRM'] = 'false'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_conditional_model_imports():
    """Test that conditional model imports work correctly"""
    print("\n=== Testing Conditional Model Imports ===")
    
    try:
        # Import the conditional imports module
        from shared.conditional_imports import import_models
        from shared.database.connection import Base
        
        print("✓ Imported conditional_imports module")
        
        # Get initial table count
        initial_tables = len(Base.metadata.tables)
        print(f"  Initial tables registered: {initial_tables}")
        
        # Call import_models to conditionally import models
        import_models()
        print("✓ Conditional model imports completed")
        
        # Check final table count
        final_tables = len(Base.metadata.tables)
        print(f"  Final tables registered: {final_tables}")
        print(f"  Tables added: {final_tables - initial_tables}")
        
        # List all registered tables
        table_names = list(Base.metadata.tables.keys())
        print(f"\n  Registered tables ({len(table_names)}):")
        for i, table_name in enumerate(table_names[:20], 1):  # Show first 20
            print(f"    {i}. {table_name}")
        if len(table_names) > 20:
            print(f"    ... and {len(table_names) - 20} more")
        
        # Check for vendors table conflict
        vendors_tables = [t for t in table_names if 'vendor' in t.lower()]
        print(f"\n  Tables with 'vendor' in name: {vendors_tables}")
        
        # Ensure vendors table is NOT present (since ENABLE_INVENTORY and ENABLE_ACCOUNTING are false)
        if 'vendors' not in table_names:
            print("✓ No 'vendors' table conflict (both accounting and inventory disabled)")
        else:
            print("⚠️  'vendors' table found (should not be present with current config)")
            return False
        
        # Check that expected tables ARE present
        expected_tables = ['tenants', 'users', 'roles']
        missing_tables = [t for t in expected_tables if t not in table_names]
        if missing_tables:
            print(f"✗ Missing expected tables: {missing_tables}")
            return False
        else:
            print(f"✓ Core tables present: {expected_tables}")
        
        # Check customer and loan tables are present
        if 'customers' in table_names and 'loan_applications' in table_names:
            print("✓ Customer and loan tables present (modules enabled)")
        else:
            print("✗ Customer or loan tables missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_inventory_enabled():
    """Test that vendors table appears when inventory is enabled"""
    print("\n=== Testing With Inventory Enabled ===")
    
    try:
        # Enable inventory
        os.environ['ENABLE_INVENTORY'] = 'true'
        
        # Need to reload modules
        import importlib
        import sys
        
        # Remove cached modules
        modules_to_remove = [m for m in sys.modules.keys() if m.startswith('shared.') or m.startswith('backend.shared.')]
        for mod in modules_to_remove:
            del sys.modules[mod]
        
        # Reimport
        from shared.conditional_imports import import_models
        from shared.database.connection import Base
        
        # Clear existing tables
        Base.metadata.clear()
        
        # Import models with inventory enabled
        import_models()
        
        table_names = list(Base.metadata.tables.keys())
        print(f"  Registered tables with inventory enabled: {len(table_names)}")
        
        # Check for vendors table
        if 'vendors' in table_names:
            print("✓ 'vendors' table present (inventory enabled)")
            
            # Check for inventory_items table
            if 'inventory_items' in table_names:
                print("✓ 'inventory_items' table present")
                
                # Try to get table metadata to check foreign key
                from sqlalchemy import MetaData
                vendors_table = Base.metadata.tables.get('vendors')
                inventory_table = Base.metadata.tables.get('inventory_items')
                
                if vendors_table and inventory_table:
                    print("✓ Both tables accessible via metadata")
                    
                    # Check foreign keys
                    fkeys = list(inventory_table.foreign_keys)
                    vendor_fkeys = [fk for fk in fkeys if 'vendor' in str(fk.target_fullname).lower()]
                    print(f"  Foreign keys to vendors: {len(vendor_fkeys)}")
                    
                    return True
        else:
            print("✗ 'vendors' table not found (should be present)")
            return False
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING CONDITIONAL MODEL IMPORTS")
    print("=" * 60)
    
    results = {
        "Conditional Imports (Minimal)": test_conditional_model_imports(),
        "Inventory Enabled": test_with_inventory_enabled(),
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
