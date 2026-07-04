# Create Alembic Migration for Master Data Models

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Creating Master Data Migration" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Navigate to backend
Set-Location backend

# Activate virtual environment
Write-Host "🔹 Activating virtual environment..." -ForegroundColor Blue
& .\venv\Scripts\Activate.ps1

Write-Host "🔹 Creating migration for master data models..." -ForegroundColor Blue

# Create migration
alembic revision --autogenerate -m "Add master data models (geography, banking, financial, configuration)"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migration created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Review the migration file in database/migrations/versions/" -ForegroundColor White
    Write-Host "   2. Run: alembic upgrade head" -ForegroundColor White
    Write-Host "   3. Or use: .\scripts\seed-master-data.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Migration creation failed!" -ForegroundColor Red
    Write-Host ""
}

# Return to project root
Set-Location ..
