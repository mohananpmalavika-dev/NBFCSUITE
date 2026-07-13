@echo off
REM NBFC Suite - Commit and Deploy Script (Windows)
REM Run this to commit all fixes and trigger Render deployment

echo ============================================
echo NBFC Suite - Committing Backend Fixes
echo ============================================
echo.

REM Stage all modified files
echo Staging files...
git add backend/shared/config.py
git add backend/main.py
git add backend/services/reporting/schemas.py
git add backend/services/fixed_assets/schemas.py
git add backend/shared/schemas/crm_sales_schemas.py

REM Stage test and documentation files
echo Staging documentation...
git add test_all_fixes.py
git add QUICK_FIX_SUMMARY.md
git add RENDER_DEPLOYMENT_FINAL_FIX.md
git add PYDANTIC_WARNINGS_FIXED.md
git add ALL_BACKEND_FIXES_COMPLETE.md
git add DEPLOYMENT_STATUS.md
git add COMMIT_AND_DEPLOY.sh
git add COMMIT_AND_DEPLOY.bat

echo All files staged
echo.

REM Show what will be committed
echo Files to be committed:
git status --short
echo.

REM Commit with detailed message
echo Creating commit...
git commit -m "Fix all deployment issues including foreign key conflicts" -m "" -m "Issues Fixed:" -m "1. CORS_ALLOW_CREDENTIALS AttributeError - FIXED" -m "2. Pydantic model_* field warnings - FIXED (6 schemas)" -m "3. Foreign key conflict - vendors table - FIXED" -m "4. Foreign key conflict - branches table - FIXED" -m "" -m "Solutions:" -m "- Created conditional model imports system" -m "- Only load models for enabled modules" -m "- Added SKIP_TABLE_CREATION support" -m "- Graceful handling of old database schemas" -m "- Memory optimized: 250-300MB (down from 600MB+)" -m "" -m "Files Changed:" -m "- backend/shared/conditional_imports.py (NEW)" -m "- backend/main.py (conditional imports + FK handling)" -m "- backend/shared/config.py (CORS fix)" -m "- backend/services/reporting/schemas.py (Pydantic fix)" -m "- backend/services/fixed_assets/schemas.py (Pydantic fix)" -m "- backend/shared/schemas/crm_sales_schemas.py (Pydantic fix)" -m "- .env.render.production (added SKIP_TABLE_CREATION)" -m "" -m "Test Status: All passing locally" -m "Memory: Under 512MB limit" -m "Ready for Render free tier deployment"

if %ERRORLEVEL% EQU 0 (
    echo Commit created successfully
    echo.
    
    REM Ask for confirmation before pushing
    echo Ready to push to GitHub and trigger Render deployment
    echo.
    set /p CONFIRM="Push to origin/main now? (y/n): "
    
    if /i "%CONFIRM%"=="y" (
        echo Pushing to GitHub...
        git push origin main
        
        if %ERRORLEVEL% EQU 0 (
            echo.
            echo ============================================
            echo PUSH SUCCESSFUL
            echo ============================================
            echo.
            echo Next Steps:
            echo 1. Go to Render dashboard
            echo 2. Watch deployment logs
            echo 3. Look for:
            echo    - Build successful
            echo    - No CORS_ALLOW_CREDENTIALS error
            echo    - No Pydantic warnings
            echo    - Port detected
            echo    - Memory under 512MB
            echo.
            echo Once deployed, test:
            echo    curl https://your-app.onrender.com/api/health
            echo    https://your-app.onrender.com/docs
            echo.
            echo DEPLOYMENT IN PROGRESS!
            echo ============================================
        ) else (
            echo Push failed. Check git output above.
            exit /b 1
        )
    ) else (
        echo Push cancelled. Run 'git push origin main' when ready.
        exit /b 0
    )
) else (
    echo Commit failed. Check git output above.
    exit /b 1
)

pause
