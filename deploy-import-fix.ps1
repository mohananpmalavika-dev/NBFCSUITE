#!/usr/bin/env pwsh
# PowerShell script to deploy the import fix
# Run this from the project root: .\deploy-import-fix.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NBFC Suite - Deploy Import Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "❌ Error: Not in a git repository" -ForegroundColor Red
    Write-Host "   Please run this script from the project root directory" -ForegroundColor Yellow
    exit 1
}

# Show current status
Write-Host "📊 Current Git Status:" -ForegroundColor Blue
Write-Host ""
git status --short
Write-Host ""

# Ask for confirmation
Write-Host "This will commit and push the import fixes to resolve the deployment error." -ForegroundColor Yellow
Write-Host ""
$confirmation = Read-Host "Continue? (Y/N)"

if ($confirmation -ne 'Y' -and $confirmation -ne 'y') {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "📝 Staging files..." -ForegroundColor Blue

# Stage the fixed service files
git add backend/services/credit_policy/credit_policy_models.py
git add backend/services/credit_policy/credit_policy_router.py
git add backend/services/product_lifecycle/product_lifecycle_models.py
git add backend/services/product_lifecycle/product_lifecycle_router.py
git add backend/services/rules/rules_models.py
git add backend/services/rules/rules_router.py
git add backend/services/workflow/workflow_models.py
git add backend/services/workflow/workflow_router.py

# Stage documentation files
git add DEPLOYMENT_IMPORT_FIX_COMPLETE.md
git add DEPLOY_AFTER_FIX.md
git add verify_imports.py
git add deploy-import-fix.ps1

Write-Host "✅ Files staged" -ForegroundColor Green
Write-Host ""

# Create commit
Write-Host "💾 Creating commit..." -ForegroundColor Blue
$commitMessage = @"
fix: resolve ModuleNotFoundError by correcting backend.core to backend.shared imports

- Fixed imports in credit_policy, product_lifecycle, rules, and workflow modules
- Changed backend.core.database to backend.shared.database.connection
- Changed backend.core.auth to backend.services.auth.dependencies
- All 8 affected files now use correct import paths
- Resolves deployment failure on Render

Files changed:
- backend/services/credit_policy/credit_policy_models.py
- backend/services/credit_policy/credit_policy_router.py
- backend/services/product_lifecycle/product_lifecycle_models.py
- backend/services/product_lifecycle/product_lifecycle_router.py
- backend/services/rules/rules_models.py
- backend/services/rules/rules_router.py
- backend/services/workflow/workflow_models.py
- backend/services/workflow/workflow_router.py
"@

git commit -m $commitMessage

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Commit failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Commit created" -ForegroundColor Green
Write-Host ""

# Push to remote
Write-Host "🚀 Pushing to remote..." -ForegroundColor Blue
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Push failed" -ForegroundColor Red
    Write-Host "   You may need to pull changes first or check your remote configuration" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ Deployment Triggered Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open Render Dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "   2. Navigate to 'nbfc-backend' service" -ForegroundColor White
Write-Host "   3. Watch the deployment logs" -ForegroundColor White
Write-Host "   4. Deployment should complete in ~5-7 minutes" -ForegroundColor White
Write-Host ""
Write-Host "🔍 What to watch for:" -ForegroundColor Cyan
Write-Host "   ✅ Build completing without import errors" -ForegroundColor Green
Write-Host "   ✅ 'Starting NBFC Financial Suite API...' message" -ForegroundColor Green
Write-Host "   ✅ Health check passing" -ForegroundColor Green
Write-Host ""
Write-Host "📖 See DEPLOY_AFTER_FIX.md for detailed monitoring instructions" -ForegroundColor Yellow
Write-Host ""
