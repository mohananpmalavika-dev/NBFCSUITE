# Script to create initial database migration
# This creates the migration file for tenants, users, roles, and permissions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Creating Initial Database Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend
Set-Location C:\NBFCSUITE\backend

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Create migration
Write-Host "Creating Alembic migration..." -ForegroundColor Yellow
alembic revision --autogenerate -m "initial schema - tenants, users, roles, permissions"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migration created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Review migration file in database/migrations/versions/" -ForegroundColor White
    Write-Host "2. Run: alembic upgrade head" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "✗ Migration creation failed" -ForegroundColor Red
    exit 1
}
