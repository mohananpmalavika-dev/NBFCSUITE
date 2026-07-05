# NBFC Financial Suite - Development Startup Script
# This script automatically sets up and runs both backend and frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NBFC Financial Suite - Dev Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

if (-not (Test-Command python)) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/" -ForegroundColor Red
    exit 1
}

if (-not (Test-Command node)) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js 20+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python found: $(python --version)" -ForegroundColor Green
Write-Host "✓ Node.js found: $(node --version)" -ForegroundColor Green
Write-Host ""

# Backend Setup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setting up Backend..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location backend

# Check if virtual environment exists
if (-not (Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Installing/Updating Python dependencies..." -ForegroundColor Yellow
& ".\venv\Scripts\pip.exe" install --upgrade pip -q
& ".\venv\Scripts\pip.exe" install -r requirements.txt -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install Python dependencies" -ForegroundColor Red
    Set-Location ..
    exit 1
}
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ .env file created" -ForegroundColor Green
        Write-Host "⚠ Please update .env with your database credentials" -ForegroundColor Yellow
    } else {
        Write-Host "⚠ .env.example not found. Creating basic .env..." -ForegroundColor Yellow
        @"
APP_NAME=NBFC Financial Suite
APP_ENV=development
APP_DEBUG=true

DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/nbfc_dev
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nbfc_dev
DB_USER=postgres
DB_PASSWORD=password

SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=http://localhost:3000
CORS_ALLOW_CREDENTIALS=true

TENANT_ISOLATION_ENABLED=true
DEFAULT_TENANT=default

UPLOAD_DIR=uploads
MAX_FILE_SIZE=10485760
MAX_FILES_PER_UPLOAD=10
"@ | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✓ Basic .env file created" -ForegroundColor Green
    }
}

# Check database connection (optional)
Write-Host "Checking database connection..." -ForegroundColor Yellow
$dbCheck = & ".\venv\Scripts\python.exe" -c @"
import asyncpg
import asyncio
async def check():
    try:
        conn = await asyncpg.connect('postgresql://postgres:password@localhost:5432/postgres')
        await conn.close()
        return True
    except:
        return False
print(asyncio.run(check()))
"@ 2>$null

if ($dbCheck -eq "True") {
    Write-Host "✓ Database connection successful" -ForegroundColor Green
} else {
    Write-Host "⚠ Could not connect to database. Make sure PostgreSQL is running." -ForegroundColor Yellow
    Write-Host "  You may need to create the database: createdb nbfc_dev" -ForegroundColor Yellow
}

# Run migrations
Write-Host "Running database migrations..." -ForegroundColor Yellow
& ".\venv\Scripts\alembic.exe" upgrade head 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database migrations completed" -ForegroundColor Green
} else {
    Write-Host "⚠ Migration failed. Database may need to be created first." -ForegroundColor Yellow
}

Set-Location ..

# Frontend Setup
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setting up Frontend..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Set-Location "frontend\apps\admin-portal"

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    npm install --legacy-peer-deps --loglevel=error
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install Node.js dependencies" -ForegroundColor Red
        Set-Location ..\..\..
        exit 1
    }
    Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
} else {
    Write-Host "✓ Node.js dependencies already installed" -ForegroundColor Green
}

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env.local"
    } else {
        "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" | Out-File -FilePath ".env.local" -Encoding UTF8
    }
    Write-Host "✓ .env.local file created" -ForegroundColor Green
}

Set-Location ..\..\..

# Start servers
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Servers..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\activate; Write-Host 'Backend Server Starting...' -ForegroundColor Green; python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

Write-Host "✓ Backend server starting in new window" -ForegroundColor Green
Write-Host "  Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs (Swagger): http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 3

Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend\apps\admin-portal'; Write-Host 'Frontend Server Starting...' -ForegroundColor Green; npm run dev"

Write-Host "✓ Frontend server starting in new window" -ForegroundColor Green
Write-Host "  Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Servers Starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please wait 10-20 seconds for servers to start." -ForegroundColor Yellow
Write-Host ""
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "  • Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "  • Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "  • API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host "  • ReDoc:        http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor Cyan
Write-Host "  • Username: admin" -ForegroundColor White
Write-Host "  • Password: admin123" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to open the application in your browser..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✓ Application opened in browser" -ForegroundColor Green
Write-Host ""
Write-Host "To stop the servers, close the PowerShell windows or press Ctrl+C in each." -ForegroundColor Yellow
Write-Host ""
