# NBFC Financial Suite - Database Setup Script
# Creates database and runs initial migrations

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$dbName = "nbfc_dev"
$dbUser = "postgres"
$dbPassword = "password"

Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Create database: $dbName" -ForegroundColor White
Write-Host "  2. Run database migrations" -ForegroundColor White
Write-Host "  3. Create initial admin user (optional)" -ForegroundColor White
Write-Host ""

# Ask for database password
Write-Host "Enter PostgreSQL password for user '$dbUser':" -ForegroundColor Yellow
$securePassword = Read-Host -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$dbPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

Write-Host ""

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $dbPassword

# Check if database exists
Write-Host "Checking if database exists..." -ForegroundColor Yellow
$dbExists = psql -U $dbUser -lqt | Select-String -Pattern "^\s*$dbName\s*\|"

if ($dbExists) {
    Write-Host "  ⚠ Database '$dbName' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to drop and recreate it? (yes/no)"
    if ($response -eq "yes") {
        Write-Host "  Dropping database..." -ForegroundColor Yellow
        dropdb -U $dbUser $dbName 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Database dropped" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Failed to drop database" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "  Keeping existing database" -ForegroundColor Yellow
        $skipCreate = $true
    }
}

# Create database
if (-not $skipCreate) {
    Write-Host "Creating database '$dbName'..." -ForegroundColor Yellow
    createdb -U $dbUser $dbName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Database created successfully" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Failed to create database" -ForegroundColor Red
        Write-Host "  Make sure PostgreSQL is running and credentials are correct" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Update .env file
Write-Host "Updating .env file..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

# Update DATABASE_URL in .env
$envContent = Get-Content ".env"
$envContent = $envContent -replace "DATABASE_URL=.*", "DATABASE_URL=postgresql+asyncpg://$dbUser`:$dbPassword@localhost:5432/$dbName"
$envContent = $envContent -replace "DB_NAME=.*", "DB_NAME=$dbName"
$envContent = $envContent -replace "DB_USER=.*", "DB_USER=$dbUser"
$envContent = $envContent -replace "DB_PASSWORD=.*", "DB_PASSWORD=$dbPassword"
$envContent | Set-Content ".env"

Write-Host "  ✓ .env file updated" -ForegroundColor Green
Write-Host ""

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
& ".\venv\Scripts\activate.ps1"
& ".\venv\Scripts\alembic.exe" upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Migrations completed successfully" -ForegroundColor Green
} else {
    Write-Host "  ✗ Migration failed" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database Details:" -ForegroundColor Yellow
Write-Host "  • Name: $dbName" -ForegroundColor White
Write-Host "  • User: $dbUser" -ForegroundColor White
Write-Host "  • Host: localhost" -ForegroundColor White
Write-Host "  • Port: 5432" -ForegroundColor White
Write-Host ""
Write-Host "You can now start the application with: .\start-dev.bat" -ForegroundColor Green
Write-Host ""

# Clear password from environment
$env:PGPASSWORD = $null
