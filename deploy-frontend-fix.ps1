#!/usr/bin/env pwsh
# PowerShell script to deploy the frontend fix
# Run this from the project root: .\deploy-frontend-fix.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Frontend Build Fix - Deployment" -ForegroundColor Cyan
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

Write-Host "Fix Applied:" -ForegroundColor Yellow
Write-Host "  ✅ Added missing mutations (checkEligibility, submitApplication, calculateSettlement)" -ForegroundColor Green
Write-Host "  ✅ Added helper functions (getStatusBadge, getProgressPercentage)" -ForegroundColor Green
Write-Host "  ✅ Added proper return statement with JSX structure" -ForegroundColor Green
Write-Host "  ✅ Fixed syntax error in surrender page" -ForegroundColor Green
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Continue with deployment? (Y/N)"

if ($confirmation -ne 'Y' -and $confirmation -ne 'y') {
    Write-Host "❌ Deployment cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "📝 Staging files..." -ForegroundColor Blue

# Stage the fixed file
git add frontend/apps/admin-portal/src/app/lockers/surrender/page.tsx
git add FRONTEND_BUILD_FIX_COMPLETE.md
git add deploy-frontend-fix.ps1
git add deploy-frontend-fix.bat

Write-Host "✅ Files staged" -ForegroundColor Green
Write-Host ""

# Create commit
Write-Host "💾 Creating commit..." -ForegroundColor Blue
$commitMessage = @"
fix: add missing mutations and return statement in surrender page

- Added checkEligibilityMutation for checking surrender eligibility
- Added submitApplicationMutation for submitting new applications
- Added calculateSettlementMutation for calculating final settlement
- Added getStatusBadge helper function for status badges
- Added getProgressPercentage helper function for progress tracking
- Added proper return statement with complete JSX structure
- Fixed syntax error that was blocking frontend build

Resolves: Webpack syntax error in locker surrender page
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
Write-Host "  ✅ Frontend Fix Deployed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open Render Dashboard: https://dashboard.render.com" -ForegroundColor White
Write-Host "   2. Navigate to 'nbfc-frontend' service" -ForegroundColor White
Write-Host "   3. Watch the build logs" -ForegroundColor White
Write-Host "   4. Build should complete in ~5-10 minutes" -ForegroundColor White
Write-Host ""
Write-Host "🔍 What to watch for:" -ForegroundColor Cyan
Write-Host "   ✅ No syntax errors in webpack" -ForegroundColor Green
Write-Host "   ✅ 'Compiled successfully' message" -ForegroundColor Green
Write-Host "   ✅ Build completes without errors" -ForegroundColor Green
Write-Host "   ✅ Service goes live" -ForegroundColor Green
Write-Host ""
Write-Host "📖 See FRONTEND_BUILD_FIX_COMPLETE.md for details" -ForegroundColor Yellow
Write-Host ""
