@echo off
echo ========================================
echo Directory Check - SupplyLine MRO Suite
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

echo Script location: %SCRIPT_DIR%
echo.

REM Navigate to the script directory
cd /d "%SCRIPT_DIR%"

echo Current directory after navigation: %CD%
echo.

echo Listing directory contents:
echo ========================================
dir /b
echo.

echo Checking for key files:
echo ========================================

if exist "package.json" (
    echo ✓ package.json - FOUND
) else (
    echo ✗ package.json - MISSING
)

if exist "frontend" (
    echo ✓ frontend folder - FOUND
) else (
    echo ✗ frontend folder - MISSING
)

if exist "backend" (
    echo ✓ backend folder - FOUND
) else (
    echo ✗ backend folder - MISSING
)

if exist "electron" (
    echo ✓ electron folder - FOUND
) else (
    echo ✗ electron folder - MISSING
)

if exist "node_modules" (
    echo ✓ node_modules folder - FOUND
) else (
    echo ✗ node_modules folder - MISSING
)

echo.
echo ========================================
echo Directory Check Complete
echo ========================================
echo.
echo This window will stay open so you can see the results.
echo Press any key when you're ready to close...
pause >nul
