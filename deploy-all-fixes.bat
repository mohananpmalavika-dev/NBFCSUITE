@echo off
REM Batch script to deploy ALL fixes (Backend + Frontend)

echo.
echo ============================================================
echo   NBFC Suite - Complete Deployment Fix
echo   Backend Import Errors + Frontend Syntax Errors
echo ============================================================
echo.

REM Check if we're in a git repository
if not exist ".git" (
    echo [ERROR] Not in a git repository
    echo         Please run this script from the project root directory
    exit /b 1
)

echo [INFO] Git Status:
echo.
git status --short
echo.

echo ============================================================
echo FIXES APPLIED:
echo ============================================================
echo.

echo [BACKEND] Backend Fix (8 files):
echo   [OK] Credit Policy: models + router
echo   [OK] Product Lifecycle: models + router
echo   [OK] Rules Engine: models + router
echo   [OK] Workflow Engine: models + router
echo   Changed: backend.core to backend.shared imports
echo.

echo [FRONTEND] Frontend Fix (1 file):
echo   [OK] Surrender Page: mutations + helpers + return (~180 lines)
echo.

echo ============================================================
echo.

set /p confirmation="Continue with deployment? (Y/N): "
if /i not "%confirmation%"=="Y" (
    echo.
    echo [CANCELLED] Deployment cancelled
    exit /b 0
)

echo.
echo [INFO] Staging all fixed files...

REM Stage backend fixes
git add backend/services/credit_policy/
git add backend/services/product_lifecycle/
git add backend/services/rules/
git add backend/services/workflow/

REM Stage frontend fixes
git add frontend/apps/admin-portal/src/app/lockers/surrender/page.tsx

REM Stage documentation and scripts
git add *.md *.txt *.ps1 *.bat *.py

echo [SUCCESS] All files staged
echo.

echo [INFO] Creating commit...
git commit -m "fix: resolve all deployment errors (backend + frontend)" -m "Backend: Fixed imports from backend.core to backend.shared (8 files)" -m "Frontend: Added missing mutations and return statement (1 file)" -m "Docs: Added comprehensive guides and scripts" -m "Total: 9 code files + 9 docs + 7 scripts"

if errorlevel 1 (
    echo [ERROR] Commit failed
    exit /b 1
)

echo [SUCCESS] Commit created
echo.

echo [INFO] Pushing to remote...
git push origin main

if errorlevel 1 (
    echo [ERROR] Push failed
    echo         Try: git pull origin main --rebase
    exit /b 1
)

echo.
echo ============================================================
echo   SUCCESS - ALL FIXES DEPLOYED!
echo ============================================================
echo.

echo NEXT STEPS:
echo   1. Open Render Dashboard: https://dashboard.render.com
echo   2. Monitor nbfc-backend (~5-7 min)
echo   3. Monitor nbfc-frontend (~7-10 min)
echo   4. Test endpoints after deployment
echo.

echo TIMELINE:
echo   Backend:  5-7 minutes
echo   Frontend: 7-10 minutes
echo   Total:    ~15 minutes
echo.

echo DOCS:
echo   Overview: 00_BOTH_FIXES_SUMMARY.md
echo   Backend:  00_DEPLOYMENT_FIX_INDEX.md
echo   Frontend: FRONTEND_BUILD_FIX_COMPLETE.md
echo   Issues:   TROUBLESHOOTING_GUIDE.md
echo.

echo Deployment initiated! Watch Render for progress.
echo.
pause
