@echo off
REM Batch script to deploy the import fix
REM Run this from the project root: deploy-import-fix.bat

echo.
echo ========================================
echo   NBFC Suite - Deploy Import Fix
echo ========================================
echo.

REM Check if we're in a git repository
if not exist ".git" (
    echo [ERROR] Not in a git repository
    echo         Please run this script from the project root directory
    exit /b 1
)

REM Show current status
echo [INFO] Current Git Status:
echo.
git status --short
echo.

REM Ask for confirmation
set /p confirmation="Continue? (Y/N): "
if /i not "%confirmation%"=="Y" (
    echo [CANCELLED] Deployment cancelled
    exit /b 0
)

echo.
echo [INFO] Staging files...

REM Stage the fixed service files
git add backend/services/credit_policy/credit_policy_models.py
git add backend/services/credit_policy/credit_policy_router.py
git add backend/services/product_lifecycle/product_lifecycle_models.py
git add backend/services/product_lifecycle/product_lifecycle_router.py
git add backend/services/rules/rules_models.py
git add backend/services/rules/rules_router.py
git add backend/services/workflow/workflow_models.py
git add backend/services/workflow/workflow_router.py

REM Stage documentation files
git add DEPLOYMENT_IMPORT_FIX_COMPLETE.md
git add DEPLOY_AFTER_FIX.md
git add verify_imports.py
git add deploy-import-fix.ps1
git add deploy-import-fix.bat

echo [SUCCESS] Files staged
echo.

REM Create commit
echo [INFO] Creating commit...
git commit -m "fix: resolve ModuleNotFoundError by correcting backend.core to backend.shared imports" -m "- Fixed imports in credit_policy, product_lifecycle, rules, and workflow modules" -m "- Changed backend.core.database to backend.shared.database.connection" -m "- Changed backend.core.auth to backend.services.auth.dependencies" -m "- All 8 affected files now use correct import paths" -m "- Resolves deployment failure on Render"

if errorlevel 1 (
    echo [ERROR] Commit failed
    exit /b 1
)

echo [SUCCESS] Commit created
echo.

REM Push to remote
echo [INFO] Pushing to remote...
git push origin main

if errorlevel 1 (
    echo [ERROR] Push failed
    echo         You may need to pull changes first or check your remote configuration
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS - Deployment Triggered!
echo ========================================
echo.
echo Next Steps:
echo   1. Open Render Dashboard: https://dashboard.render.com
echo   2. Navigate to 'nbfc-backend' service
echo   3. Watch the deployment logs
echo   4. Deployment should complete in ~5-7 minutes
echo.
echo What to watch for:
echo   [OK] Build completing without import errors
echo   [OK] 'Starting NBFC Financial Suite API...' message
echo   [OK] Health check passing
echo.
echo See DEPLOY_AFTER_FIX.md for detailed monitoring instructions
echo.
pause
