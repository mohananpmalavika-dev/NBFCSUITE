#!/usr/bin/env python3
"""
Verification Script - Test All Fixes Before Deployment
Run this script to verify all fixes are working correctly
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing Python imports...")
    
    tests = []
    
    # Test 1: NBFC Loan Models
    try:
        from backend.shared.database.loan_models import (
            LoanAccount, LoanApplication, LoanApprovalWorkflow, 
            LoanRepayment, LoanProduct, LoanEMISchedule
        )
        tests.append(("✅", "NBFC loan models"))
    except ImportError as e:
        tests.append(("❌", f"NBFC loan models: {e}"))
    
    # Test 2: HRMS Loan Models
    try:
        from backend.shared.database.hrms_loan_models import (
            EmployeeLoan, LoanPolicy, LoanEMISchedule as HRMSEMISchedule,
            LoanTransaction, LoanType, LoanStatus
        )
        tests.append(("✅", "HRMS loan models"))
    except ImportError as e:
        tests.append(("❌", f"HRMS loan models: {e}"))
    
    # Test 3: Notification Models
    try:
        from backend.shared.database.notification_models import (
            Notification, NotificationAnalytics, NotificationProvider,
            DLTEntity, DLTTemplate, DLTConsent
        )
        tests.append(("✅", "Notification models"))
    except ImportError as e:
        tests.append(("❌", f"Notification models: {e}"))
    
    # Test 4: Dashboard Router
    try:
        from backend.services.dashboard.router import router
        tests.append(("✅", "Dashboard router"))
    except ImportError as e:
        tests.append(("❌", f"Dashboard router: {e}"))
    
    # Test 5: HRMS Loan Service
    try:
        from backend.services.hrms.loan_service import LoanService
        tests.append(("✅", "HRMS loan service"))
    except ImportError as e:
        tests.append(("❌", f"HRMS loan service: {e}"))
    
    # Print results
    print("\n" + "="*50)
    print("IMPORT TEST RESULTS")
    print("="*50)
    for status, message in tests:
        print(f"{status} {message}")
    
    # Check if all passed
    failed = [t for t in tests if t[0] == "❌"]
    if failed:
        print(f"\n❌ {len(failed)} test(s) failed!")
        return False
    else:
        print(f"\n✅ All {len(tests)} tests passed!")
        return True


def check_requirements():
    """Check requirements files"""
    print("\n🔍 Checking requirements files...")
    
    checks = []
    
    # Check requirements.txt
    try:
        with open('backend/requirements.txt', 'r') as f:
            content = f.read()
            if 'jinja2' in content:
                checks.append(("✅", "jinja2 in requirements.txt"))
            else:
                checks.append(("❌", "jinja2 NOT in requirements.txt"))
    except Exception as e:
        checks.append(("❌", f"Error reading requirements.txt: {e}"))
    
    # Check requirements.render.txt
    try:
        with open('backend/requirements.render.txt', 'r') as f:
            content = f.read()
            if 'jinja2' in content:
                checks.append(("✅", "jinja2 in requirements.render.txt (CRITICAL!)"))
            else:
                checks.append(("❌", "jinja2 NOT in requirements.render.txt (CRITICAL!)"))
    except Exception as e:
        checks.append(("❌", f"Error reading requirements.render.txt: {e}"))
    
    # Print results
    print("\n" + "="*50)
    print("REQUIREMENTS CHECK")
    print("="*50)
    for status, message in checks:
        print(f"{status} {message}")
    
    # Check if all passed
    failed = [c for c in checks if c[0] == "❌"]
    if failed:
        print(f"\n❌ {len(failed)} check(s) failed!")
        return False
    else:
        print(f"\n✅ All {len(checks)} checks passed!")
        return True


def check_files_exist():
    """Check that all expected files exist"""
    print("\n🔍 Checking file existence...")
    
    files = [
        ('backend/shared/database/hrms_loan_models.py', 'HRMS loan models (NEW)'),
        ('backend/shared/database/loan_models.py', 'NBFC loan models'),
        ('backend/shared/database/notification_models.py', 'Notification models'),
        ('backend/services/dashboard/router.py', 'Dashboard router'),
        ('backend/services/hrms/loan_service.py', 'HRMS loan service'),
        ('backend/requirements.txt', 'Development requirements'),
        ('backend/requirements.render.txt', 'Render requirements'),
    ]
    
    checks = []
    for filepath, description in files:
        if os.path.exists(filepath):
            checks.append(("✅", f"{description}"))
        else:
            checks.append(("❌", f"{description} NOT FOUND: {filepath}"))
    
    # Print results
    print("\n" + "="*50)
    print("FILE EXISTENCE CHECK")
    print("="*50)
    for status, message in checks:
        print(f"{status} {message}")
    
    # Check if all passed
    failed = [c for c in checks if c[0] == "❌"]
    if failed:
        print(f"\n❌ {len(failed)} file(s) missing!")
        return False
    else:
        print(f"\n✅ All {len(checks)} files exist!")
        return True


def main():
    """Run all verification tests"""
    print("="*50)
    print("DEPLOYMENT VERIFICATION SCRIPT")
    print("="*50)
    print("This script verifies all fixes are in place\n")
    
    # Run all tests
    results = []
    
    print("📋 Running verification tests...\n")
    
    results.append(("File Check", check_files_exist()))
    results.append(("Requirements Check", check_requirements()))
    results.append(("Import Tests", test_imports()))
    
    # Final summary
    print("\n" + "="*50)
    print("FINAL SUMMARY")
    print("="*50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("="*50)
        print("\n✅ Your code is ready to deploy!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Fix: Resolve import errors and add dependencies'")
        print("3. git push origin main")
        print("\n🚀 Deploy and watch it succeed!")
        return 0
    else:
        print("❌ SOME CHECKS FAILED!")
        print("="*50)
        print("\n⚠️  Please fix the issues above before deploying.")
        print("Review the error messages and fix the failing checks.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
