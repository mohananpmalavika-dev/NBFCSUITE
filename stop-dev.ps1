# NBFC Financial Suite - Stop Development Servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Stopping NBFC Suite Servers..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop backend (uvicorn)
Write-Host "Stopping Backend Server..." -ForegroundColor Yellow
$backendProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*backend.main:app*"
}

if ($backendProcesses) {
    $backendProcesses | Stop-Process -Force
    Write-Host "✓ Backend server stopped" -ForegroundColor Green
} else {
    Write-Host "✓ Backend server not running" -ForegroundColor Gray
}

# Stop frontend (npm/node)
Write-Host "Stopping Frontend Server..." -ForegroundColor Yellow
$frontendProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*next dev*"
}

if ($frontendProcesses) {
    $frontendProcesses | Stop-Process -Force
    Write-Host "✓ Frontend server stopped" -ForegroundColor Green
} else {
    Write-Host "✓ Frontend server not running" -ForegroundColor Gray
}

# Also try to free up ports
Write-Host ""
Write-Host "Checking ports..." -ForegroundColor Yellow

# Check port 8000 (backend)
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    $process = Get-Process -Id $port8000.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.Id -Force
        Write-Host "✓ Freed port 8000" -ForegroundColor Green
    }
} else {
    Write-Host "✓ Port 8000 is free" -ForegroundColor Gray
}

# Check port 3000 (frontend)
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    $process = Get-Process -Id $port3000.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $process.Id -Force
        Write-Host "✓ Freed port 3000" -ForegroundColor Green
    }
} else {
    Write-Host "✓ Port 3000 is free" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All servers stopped" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
