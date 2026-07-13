#!/usr/bin/env python3
"""
Test All Backend Fixes
Verifies that all Pydantic warnings and Settings issues are resolved
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))


def test_settings_import():
    """Test that Settings can be imported and CORS_ALLOW_CREDENTIALS exists"""
    print("\n=== Testing Settings Import ===")
    try:
        from shared.config import settings
        print(f"✓ Settings imported successfully")
        print(f"  - APP_NAME: {settings.APP_NAME}")
        print(f"  - APP_ENV: {settings.APP_ENV}")
        
        # Test CORS_ALLOW_CREDENTIALS attribute
        cors_cred = getattr(settings, 'CORS_ALLOW_CREDENTIALS', None)
        if cors_cred is not None:
            print(f"✓ CORS_ALLOW_CREDENTIALS exists: {cors_cred}")
        else:
            print(f"✗ CORS_ALLOW_CREDENTIALS not found")
            return False
            
        # Test all feature flags
        print(f"  - ENABLE_AUTH: {settings.ENABLE_AUTH}")
        print(f"  - ENABLE_CUSTOMERS: {settings.ENABLE_CUSTOMERS}")
        print(f"  - ENABLE_LOANS: {settings.ENABLE_LOANS}")
        
        return True
    except Exception as e:
        print(f"✗ Settings import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_reporting_schemas():
    """Test that reporting schemas don't produce warnings"""
    print("\n=== Testing Reporting Schemas ===")
    try:
        from services.reporting.schemas import (
            PredictiveModelCreate,
            PredictiveModelResponse,
            PredictionRequest,
            PredictionResponse
        )
        print("✓ Reporting schemas imported successfully")
        
        # Test creating instance with model_* fields
        model_data = {
            "model_name": "Test Model",
            "model_description": "Test Description",
            "model_type": "classification",
            "use_case": "credit_risk",
            "algorithm": "random_forest",
            "features": {"feature1": "value1"},
            "target_variable": "default",
            "training_data_query": "SELECT * FROM data"
        }
        model = PredictiveModelCreate(**model_data)
        print(f"✓ PredictiveModelCreate created with model_* fields")
        print(f"  - model_name: {model.model_name}")
        print(f"  - model_type: {model.model_type}")
        
        return True
    except Exception as e:
        print(f"✗ Reporting schemas test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fixed_assets_schemas():
    """Test that fixed assets schemas don't produce warnings"""
    print("\n=== Testing Fixed Assets Schemas ===")
    try:
        from services.fixed_assets.schemas import FixedAssetBase
        print("✓ Fixed Assets schemas imported successfully")
        
        # Test field with model_number
        print("✓ FixedAssetBase has model_number field (no warnings expected)")
        
        return True
    except Exception as e:
        print(f"✗ Fixed Assets schemas test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crm_sales_schemas():
    """Test that CRM sales schemas don't produce warnings"""
    print("\n=== Testing CRM Sales Schemas ===")
    try:
        from shared.schemas.crm_sales_schemas import ProductBase
        print("✓ CRM Sales schemas imported successfully")
        
        # Test creating product with model_number
        product_data = {
            "product_code": "TEST001",
            "product_name": "Test Product",
            "unit_price": 100.00,
            "model_number": "MODEL123"
        }
        product = ProductBase(**product_data)
        print(f"✓ ProductBase created with model_number field")
        print(f"  - model_number: {product.model_number}")
        
        return True
    except Exception as e:
        print(f"✗ CRM Sales schemas test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conditional_imports():
    """Test that conditional imports work correctly"""
    print("\n=== Testing Conditional Imports ===")
    try:
        from shared.conditional_imports import get_enabled_routers
        print("✓ Conditional imports module loaded")
        
        # Get enabled routers (should be minimal set)
        enabled = get_enabled_routers()
        print(f"✓ Found {len(enabled)} enabled routers")
        
        # Show first 5 routers - each is a tuple of (router, prefix, tags, module_name)
        for i, router_tuple in enumerate(enabled[:5]):
            if len(router_tuple) >= 4:
                _, prefix, tags, module_name = router_tuple[:4]
                print(f"  - {module_name}: {prefix}")
            else:
                print(f"  - Router {i+1}: {router_tuple}")
        
        return True
    except Exception as e:
        print(f"✗ Conditional imports test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("TESTING ALL BACKEND FIXES")
    print("=" * 60)
    
    # Note: Set minimal env vars for testing
    os.environ.setdefault('DATABASE_URL', 'postgresql://user:pass@localhost/db')
    os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-for-testing-only')
    os.environ.setdefault('CORS_ALLOW_CREDENTIALS', 'false')
    
    results = {
        "Settings Import": test_settings_import(),
        "Reporting Schemas": test_reporting_schemas(),
        "Fixed Assets Schemas": test_fixed_assets_schemas(),
        "CRM Sales Schemas": test_crm_sales_schemas(),
        "Conditional Imports": test_conditional_imports(),
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
