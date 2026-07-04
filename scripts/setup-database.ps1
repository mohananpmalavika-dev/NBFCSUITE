# Complete Database Setup Script
# 1. Creates migration
# 2. Applies migration
# 3. Seeds default data

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NBFC Suite - Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Step 1: Checking Docker services..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Docker is not running. Please start Docker Desktop" -ForegroundColor Red
    Write-Host "Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Check if PostgreSQL is running
$postgresRunning = docker ps | Select-String "nbfc-postgres"
if (-not $postgresRunning) {
    Write-Host "✗ PostgreSQL container is not running" -ForegroundColor Red
    Write-Host "Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Docker services are running" -ForegroundColor Green
Write-Host ""

# Navigate to backend
Set-Location C:\NBFCSUITE\backend

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Step 3: Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Wait for PostgreSQL to be ready
Write-Host "Step 4: Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$dbReady = $false

while (-not $dbReady -and $attempt -lt $maxAttempts) {
    try {
        $result = docker exec nbfc-postgres pg_isready -U nbfc_admin -d nbfc_suite 2>&1
        if ($result -like "*accepting connections*") {
            $dbReady = $true
            Write-Host "✓ PostgreSQL is ready" -ForegroundColor Green
        } else {
            Start-Sleep -Seconds 2
            $attempt++
            Write-Host "." -NoNewline
        }
    } catch {
        Start-Sleep -Seconds 2
        $attempt++
        Write-Host "." -NoNewline
    }
}

if (-not $dbReady) {
    Write-Host ""
    Write-Host "✗ PostgreSQL failed to become ready" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Create migration
Write-Host "Step 5: Creating database migration..." -ForegroundColor Yellow
alembic revision --autogenerate -m "initial schema - tenants, users, roles, permissions"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migration created" -ForegroundColor Green
} else {
    Write-Host "✗ Migration creation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Apply migration
Write-Host "Step 6: Applying migration..." -ForegroundColor Yellow
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migration applied successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Migration failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Seed default data
Write-Host "Step 7: Seeding default data..." -ForegroundColor Yellow
python ..\database\seeds\001_default_tenant_and_admin.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Data seeded successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Seeding failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✓ Database Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Database Tables Created:" -ForegroundColor Cyan
Write-Host "  ✓ tenants" -ForegroundColor White
Write-Host "  ✓ users" -ForegroundColor White
Write-Host "  ✓ roles" -ForegroundColor White
Write-Host "  ✓ permissions" -ForegroundColor White
Write-Host "  ✓ user_roles" -ForegroundColor White
Write-Host "  ✓ role_permissions" -ForegroundColor White
Write-Host ""
Write-Host "Default Admin Credentials:" -ForegroundColor Cyan
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Please change the default password after first login!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start backend: uvicorn main:app --reload" -ForegroundColor White
Write-Host "  2. Visit: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  3. Test login endpoint with above credentials" -ForegroundColor White
Write-Host ""
Write-Host "View tables in pgAdmin: http://localhost:5050" -ForegroundColor Yellow
Write-Host ""
