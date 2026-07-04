# Master Data Seeding Script
# Seeds complete India master data (1.5L+ records)

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  NBFC Suite - Master Data Seeding" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Navigate to backend
Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "❌ Error: Virtual environment not found" -ForegroundColor Red
    Write-Host "   Please run: python -m venv venv" -ForegroundColor Yellow
    Set-Location ..
    exit 1
}

Write-Host "🔹 Activating virtual environment..." -ForegroundColor Blue
& .\venv\Scripts\Activate.ps1

Write-Host "🔹 Running Alembic migrations..." -ForegroundColor Blue
alembic upgrade head

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Migration failed!" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Write-Host ""
Write-Host "🔹 Seeding master data..." -ForegroundColor Blue
Write-Host "   This will take 30-60 seconds..." -ForegroundColor Yellow
Write-Host ""

# Run seed script
python ..\database\seeds\002_master_data_india.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  ✅ MASTER DATA SEEDED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 You now have:" -ForegroundColor Cyan
    Write-Host "   • 36 States and Union Territories" -ForegroundColor White
    Write-Host "   • 130+ Major Cities" -ForegroundColor White
    Write-Host "   • Pincode database" -ForegroundColor White
    Write-Host "   • 25+ Major Banks" -ForegroundColor White
    Write-Host "   • Bank branches with IFSC codes" -ForegroundColor White
    Write-Host "   • Loan product types" -ForegroundColor White
    Write-Host "   • Document types" -ForegroundColor White
    Write-Host "   • Occupations & Industries" -ForegroundColor White
    Write-Host "   • 2026 Holiday calendar" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 Ready for smart customer onboarding!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Master data seeding failed!" -ForegroundColor Red
    Write-Host "   Check the error messages above" -ForegroundColor Yellow
    Write-Host ""
}

# Return to project root
Set-Location ..
