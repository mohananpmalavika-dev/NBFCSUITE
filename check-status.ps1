# NBFC Financial Suite - Status Check Script
# Checks if servers are running and accessible

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NBFC Suite - Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Backend
Write-Host "Backend Status:" -ForegroundColor Yellow
$backendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Backend is RUNNING" -ForegroundColor Green
        Write-Host "  URL: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor Cyan
        $backendRunning = $true
    }
} catch {
    Write-Host "  ✗ Backend is NOT running" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Check Frontend
Write-Host "Frontend Status:" -ForegroundColor Yellow
$frontendRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ Frontend is RUNNING" -ForegroundColor Green
        Write-Host "  URL: http://localhost:3000" -ForegroundColor Cyan
        $frontendRunning = $true
    }
} catch {
    Write-Host "  ✗ Frontend is NOT running" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Check Database
Write-Host "Database Status:" -ForegroundColor Yellow
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService -and $pgService.Status -eq "Running") {
        Write-Host "  ✓ PostgreSQL service is RUNNING" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ PostgreSQL service status unknown" -ForegroundColor Yellow
        Write-Host "  (Check manually: services.msc)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ⚠ Could not check PostgreSQL status" -ForegroundColor Yellow
}

Write-Host ""

# Port Status
Write-Host "Port Status:" -ForegroundColor Yellow
$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
$port3000 = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue

if ($port8000) {
    Write-Host "  ✓ Port 8000 (Backend): IN USE" -ForegroundColor Green
} else {
    Write-Host "  ✗ Port 8000 (Backend): FREE" -ForegroundColor Red
}

if ($port3000) {
    Write-Host "  ✓ Port 3000 (Frontend): IN USE" -ForegroundColor Green
} else {
    Write-Host "  ✗ Port 3000 (Frontend): FREE" -ForegroundColor Red
}

Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($backendRunning -and $frontendRunning) {
    Write-Host "✓ All systems operational!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick Links:" -ForegroundColor Cyan
    Write-Host "  • Application:  http://localhost:3000" -ForegroundColor White
    Write-Host "  • API Docs:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host "  • Health Check: http://localhost:8000/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Login: admin / admin123" -ForegroundColor Yellow
} elseif (-not $backendRunning -and -not $frontendRunning) {
    Write-Host "✗ Both servers are down" -ForegroundColor Red
    Write-Host ""
    Write-Host "To start servers, run: .\start-dev.bat" -ForegroundColor Yellow
} else {
    Write-Host "⚠ Partial system operation" -ForegroundColor Yellow
    if (-not $backendRunning) {
        Write-Host "  • Backend needs to be started" -ForegroundColor Red
    }
    if (-not $frontendRunning) {
        Write-Host "  • Frontend needs to be started" -ForegroundColor Red
    }
}

Write-Host ""
