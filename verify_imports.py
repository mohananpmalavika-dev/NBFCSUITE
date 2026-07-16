#!/usr/bin/env python3
"""
Import Verification Script
Tests that all fixed imports work correctly
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path.parent))

def test_imports():
    """Test all the fixed imports"""
    errors = []
    
    print("🔍 Testing fixed imports...")
    print("-" * 60)
    
    # Test 1: Credit Policy Models
    try:
        from backend.services.credit_policy import credit_policy_models
        print("✅ backend.services.credit_policy.credit_policy_models")
    except ImportError as e:
        errors.append(f"❌ credit_policy_models: {e}")
        print(f"❌ backend.services.credit_policy.credit_policy_models: {e}")
    
    # Test 2: Credit Policy Router
    try:
        from backend.services.credit_policy import credit_policy_router
        print("✅ backend.services.credit_policy.credit_policy_router")
    except ImportError as e:
        errors.append(f"❌ credit_policy_router: {e}")
        print(f"❌ backend.services.credit_policy.credit_policy_router: {e}")
    
    # Test 3: Product Lifecycle Models
    try:
        from backend.services.product_lifecycle import product_lifecycle_models
        print("✅ backend.services.product_lifecycle.product_lifecycle_models")
    except ImportError as e:
        errors.append(f"❌ product_lifecycle_models: {e}")
        print(f"❌ backend.services.product_lifecycle.product_lifecycle_models: {e}")
    
    # Test 4: Product Lifecycle Router
    try:
        from backend.services.product_lifecycle import product_lifecycle_router
        print("✅ backend.services.product_lifecycle.product_lifecycle_router")
    except ImportError as e:
        errors.append(f"❌ product_lifecycle_router: {e}")
        print(f"❌ backend.services.product_lifecycle.product_lifecycle_router: {e}")
    
    # Test 5: Rules Models
    try:
        from backend.services.rules import rules_models
        print("✅ backend.services.rules.rules_models")
    except ImportError as e:
        errors.append(f"❌ rules_models: {e}")
        print(f"❌ backend.services.rules.rules_models: {e}")
    
    # Test 6: Rules Router
    try:
        from backend.services.rules import rules_router
        print("✅ backend.services.rules.rules_router")
    except ImportError as e:
        errors.append(f"❌ rules_router: {e}")
        print(f"❌ backend.services.rules.rules_router: {e}")
    
    # Test 7: Workflow Models
    try:
        from backend.services.workflow import workflow_models
        print("✅ backend.services.workflow.workflow_models")
    except ImportError as e:
        errors.append(f"❌ workflow_models: {e}")
        print(f"❌ backend.services.workflow.workflow_models: {e}")
    
    # Test 8: Workflow Router
    try:
        from backend.services.workflow import workflow_router
        print("✅ backend.services.workflow.workflow_router")
    except ImportError as e:
        errors.append(f"❌ workflow_router: {e}")
        print(f"❌ backend.services.workflow.workflow_router: {e}")
    
    print("-" * 60)
    
    if errors:
        print(f"\n❌ {len(errors)} import(s) failed:")
        for error in errors:
            print(f"   {error}")
        return False
    else:
        print(f"\n✅ All {8} imports successful!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
