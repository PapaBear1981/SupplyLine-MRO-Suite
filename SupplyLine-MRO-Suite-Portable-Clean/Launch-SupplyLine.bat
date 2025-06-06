@echo off
echo ========================================
echo SupplyLine MRO Suite - Portable Edition
echo ========================================
echo.

REM Quick Python check
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.8+ is required
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Starting SupplyLine MRO Suite...
echo.

cd /d "%~dp0App"
start "" "SupplyLine MRO Suite.exe"

echo Application launched!
echo.
echo Default login: ADMIN001 / admin123
echo.
echo Close this window after the application opens.
