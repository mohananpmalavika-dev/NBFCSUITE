@echo off
REM Batch script to deploy the frontend fix

echo.
echo ========================================
echo   Frontend Build Fix - Deployment
echo ========================================
echo.

REM Check if we're in a git repository
if not exist ".git" (
    echo [ERROR] Not in a git repository
    echo         Please run this script from the project root directory
    exit /b 1
)

echo [INFO] Current Git Status:
echo.
git status --short
echo.

echo Fix Applied:
echo   [OK] Added missing mutations (checkEligibility, submitApplication, calculateSettlement)
echo   [OK] Added helper functions (getStatusBadge, getProgressPercentage)
echo   [OK] Added proper return statement with JSX structure
echo   [OK] Fixed syntax error in surrender page
echo.

set /p confirmation="Continue with deployment? (Y/N): "
if /i not "%confirmation%"=="Y" (
    echo [CANCELLED] Deployment cancelled
    exit /b 0
)

echo.
echo [INFO] Staging files...

git add frontend/apps/admin-portal/src/app/lockers/surrender/page.tsx
git add FRONTEND_BUILD_FIX_COMPLETE.md
git add deploy-frontend-fix.ps1
git add deploy-frontend-fix.bat

echo [SUCCESS] Files staged
echo.

echo [INFO] Creating commit...
git commit -m "fix: add missing mutations and return statement in surrender page" -m "- Added checkEligibilityMutation for checking surrender eligibility" -m "- Added submitApplicationMutation for submitting new applications" -m "- Added calculateSettlementMutation for calculating final settlement" -m "- Added getStatusBadge helper function for status badges" -m "- Added getProgressPercentage helper function for progress tracking" -m "- Added proper return statement with complete JSX structure" -m "- Fixed syntax error that was blocking frontend build"

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
    echo         You may need to pull changes first
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS - Frontend Fix Deployed!
echo ========================================
echo.
echo Next Steps:
echo   1. Open Render Dashboard: https://dashboard.render.com
echo   2. Navigate to 'nbfc-frontend' service
echo   3. Watch the build logs
echo   4. Build should complete in ~5-10 minutes
echo.
echo What to watch for:
echo   [OK] No syntax errors in webpack
echo   [OK] 'Compiled successfully' message
echo   [OK] Build completes without errors
echo   [OK] Service goes live
echo.
echo See FRONTEND_BUILD_FIX_COMPLETE.md for details
echo.
pause
