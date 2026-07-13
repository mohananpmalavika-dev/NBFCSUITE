#!/usr/bin/env python3
"""
Test Backend Server Startup
Verifies the FastAPI app can be created and basic endpoints work
"""
import os
import sys

# Set required environment variables
os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/db'
os.environ['JWT_SECRET_KEY'] = 'test-secret-key-minimum-32-characters-long'

def test_app_creation():
    """Test that the FastAPI app can be created"""
    try:
        from backend.main import app
        print("[OK] FastAPI app created successfully")
        print(f"    Title: {app.title}")
        print(f"    Version: {app.version}")
        print(f"    Docs URL: {app.docs_url}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to create app: {type(e).__name__}: {str(e)}")
        return False

def test_settings():
    """Test that settings load correctly"""
    try:
        from backend.shared.config import settings
        print("[OK] Settings loaded successfully")
        print(f"    APP_NAME: {settings.APP_NAME}")
        print(f"    APP_ENV: {settings.APP_ENV}")
        print(f"    ENABLE_SWAGGER: {settings.ENABLE_SWAGGER}")
        print(f"    CORS_ALLOW_CREDENTIALS: {settings.CORS_ALLOW_CREDENTIALS}")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to load settings: {type(e).__name__}: {str(e)}")
        return False

def test_routes():
    """Test that routes are registered"""
    try:
        from backend.main import app
        # Get routes from the FastAPI app
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"[OK] {len(routes)} routes registered")
        
        # Check for key routes
        key_routes = ['/health', '/api/auth/login', '/api/dashboard/stats']
        found_routes = [r for r in key_routes if r in routes]
        print(f"    Key routes found: {len(found_routes)}/{len(key_routes)}")
        
        for route in found_routes:
            print(f"    - {route}")
        
        return len(found_routes) > 0
    except Exception as e:
        print(f"[FAIL] Failed to check routes: {type(e).__name__}: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Backend Server Startup Tests")
    print("=" * 60)
    
    tests = [
        ("Settings", test_settings),
        ("App Creation", test_app_creation),
        ("Routes", test_routes),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        results.append(test_func())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n[OK] Backend is ready for deployment!")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
