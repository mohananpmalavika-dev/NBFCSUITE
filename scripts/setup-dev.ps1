# NBFC Suite - Development Environment Setup Script
# This script sets up the complete development environment

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  NBFC Financial Suite - Development Setup" -ForegroundColor Cyan
Write-Host "  Tier-1 Enterprise Platform" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Step 1: Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✓ Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker not found. Please install Docker Desktop" -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>&1
    Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git not found. Please install Git" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Setting up environment files..." -ForegroundColor Yellow

# Copy .env.example to .env if not exists
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 3: Starting Docker containers..." -ForegroundColor Yellow

# Start Docker Compose services
docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Docker containers started successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to start Docker containers" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 4: Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "Step 5: Setting up Python backend..." -ForegroundColor Yellow

# Create Python virtual environment
Set-Location backend
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Created Python virtual environment" -ForegroundColor Green
} else {
    Write-Host "✓ Python virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment and install dependencies
& .\venv\Scripts\Activate.ps1

# Create requirements.txt if not exists
if (-not (Test-Path "requirements.txt")) {
    Write-Host "Creating requirements.txt..." -ForegroundColor Yellow
    @"
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Cache & Queue
redis==5.0.1
celery==5.3.4
kombu==5.3.4

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
bcrypt==4.1.1

# HTTP & API
httpx==0.25.2
requests==2.31.0
aiohttp==3.9.1

# Data Validation & Serialization
email-validator==2.1.0
phonenumbers==8.13.26

# Utilities
python-dotenv==1.0.0
python-dateutil==2.8.2
pytz==2023.3
pendulum==2.1.2

# Monitoring & Logging
prometheus-client==0.19.0
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0

# File Processing
python-magic==0.4.27
pillow==10.1.0
openpyxl==3.1.2
pandas==2.1.4

# PDF Processing
reportlab==4.0.7
pypdf2==3.0.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Code Quality
black==23.12.0
flake8==6.1.0
mypy==1.7.1
isort==5.13.0
"@ | Out-File -FilePath "requirements.txt" -Encoding UTF8
    Write-Host "✓ Created requirements.txt" -ForegroundColor Green
}

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "Step 6: Setting up Node.js frontend..." -ForegroundColor Yellow

Set-Location frontend

# Create package.json if not exists
if (-not (Test-Path "package.json")) {
    Write-Host "Initializing Node.js project..." -ForegroundColor Yellow
    npm init -y
    Write-Host "✓ Created package.json" -ForegroundColor Green
}

# Install dependencies
Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow

npm install --save-dev turbo typescript @types/node @types/react @types/react-dom

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Node.js dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install Node.js dependencies" -ForegroundColor Red
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "Step 7: Initializing database..." -ForegroundColor Yellow

# Wait for PostgreSQL to be ready
$maxAttempts = 30
$attempt = 0
$dbReady = $false

while (-not $dbReady -and $attempt -lt $maxAttempts) {
    try {
        $result = docker exec nbfc-postgres pg_isready -U nbfc_admin -d nbfc_suite 2>&1
        if ($result -like "*accepting connections*") {
            $dbReady = $true
            Write-Host "✓ Database is ready" -ForegroundColor Green
        } else {
            Start-Sleep -Seconds 2
            $attempt++
        }
    } catch {
        Start-Sleep -Seconds 2
        $attempt++
    }
}

if (-not $dbReady) {
    Write-Host "✗ Database failed to start" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "  Setup Complete! 🚀" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services are running:" -ForegroundColor Cyan
Write-Host "  PostgreSQL:      http://localhost:5432" -ForegroundColor White
Write-Host "  pgAdmin:         http://localhost:5050" -ForegroundColor White
Write-Host "  Redis:           http://localhost:6379" -ForegroundColor White
Write-Host "  Redis Commander: http://localhost:8081" -ForegroundColor White
Write-Host "  RabbitMQ:        http://localhost:15672" -ForegroundColor White
Write-Host "  MinIO:           http://localhost:9001" -ForegroundColor White
Write-Host "  Elasticsearch:   http://localhost:9200" -ForegroundColor White
Write-Host "  Kibana:          http://localhost:5601" -ForegroundColor White
Write-Host ""
Write-Host "Credentials:" -ForegroundColor Cyan
Write-Host "  Database User:   nbfc_admin" -ForegroundColor White
Write-Host "  Database Pass:   nbfc_secure_2026" -ForegroundColor White
Write-Host "  Redis Pass:      nbfc_redis_2026" -ForegroundColor White
Write-Host "  RabbitMQ User:   nbfc_admin / nbfc_rabbit_2026" -ForegroundColor White
Write-Host "  MinIO User:      nbfc_admin / nbfc_minio_2026" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review and update .env file with your configuration" -ForegroundColor White
Write-Host "  2. Run database migrations: cd backend && alembic upgrade head" -ForegroundColor White
Write-Host "  3. Start backend: cd backend && uvicorn main:app --reload" -ForegroundColor White
Write-Host "  4. Start frontend: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: docs/MASTER_INDEX.md" -ForegroundColor Yellow
Write-Host ""
