@echo off
echo ========================================
echo  NBFC Suite - Deploy All Fixes
echo ========================================
echo.
echo This will deploy ALL 24 fixes including:
echo - Vendor model duplicate fix
echo - Conditional imports
echo - CORS wildcard configuration
echo - And 21 other critical fixes
echo.
pause
echo.

echo [1/3] Adding all changes...
git add .

echo [2/3] Committing changes...
git commit -m "Fix: All 24 deployment issues resolved - Vendor model, CORS wildcard, conditional imports"

echo [3/3] Pushing to Render for auto-deploy...
git push origin main

echo.
echo ========================================
echo  Deployment Started!
echo ========================================
echo.
echo Next steps:
echo 1. Go to Render Dashboard
echo 2. Watch deployment logs
echo 3. Wait 2-3 minutes
echo 4. Test frontend at: https://nbfcsuite-vqel.onrender.com
echo 5. CORS errors should be GONE!
echo.
echo Backend logs should show:
echo   - "CORS configured: allow_origins=['*']"
echo   - "Conditional model imports complete"
echo   - "Application startup complete"
echo.
pause
