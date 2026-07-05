@echo off
REM NBFC Financial Suite - Quick Start Script (Windows)

echo ========================================
echo   NBFC Financial Suite - Quick Start
echo ========================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not available
    pause
    exit /b 1
)

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0start-dev.ps1"

pause
