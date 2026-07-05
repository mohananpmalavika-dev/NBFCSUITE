#!/usr/bin/env python
"""
Import Verification Script
Verifies all imports are correct after the build fixes
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test all critical imports"""
    print("🔍 Verifying imports...\n")
    
    tests = {
        "Config": "backend.shared.config",
        "Database Connection": "backend.shared.database.connection",
        "Database Models": "backend.shared.database.models",
        "Customer Models": "backend.shared.database.customer_models",
        "Loan Models": "backend.shared.database.loan_models",
        "Accounting Models": "backend.shared.database.accounting_models",
        "Security": "backend.shared.common.security",
        "Response": "backend.shared.common.response",
        "Auth Service": "backend.services.auth.service",
        "Auth Router": "backend.services.auth.router",
        "Auth Schemas": "backend.services.auth.schemas",
        "Customer Service": "backend.services.customer.service",
        "Masterdata Service": "backend.services.masterdata.service",
        "Main Application": "main",
    }
    
    failed = []
    passed = []
    
    for name, module in tests.items():
        try:
            __import__(module)
            passed.append(name)
            print(f"✅ {name:25} - OK")
        except Exception as e:
            failed.append((name, str(e)))
            print(f"❌ {name:25} - FAILED: {e}")
    
    print(f"\n{'='*60}")
    print(f"Results: {len(passed)} passed, {len(failed)} failed")
    print(f"{'='*60}\n")
    
    if failed:
        print("Failed imports:")
        for name, error in failed:
            print(f"  • {name}: {error}")
        return False
    else:
        print("🎉 All imports verified successfully!")
        return True

if __name__ == "__main__":
    try:
        success = test_imports()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
