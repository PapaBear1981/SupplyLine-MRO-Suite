@echo off
echo ========================================
echo SupplyLine MRO Suite - Simple Rebuild
echo ========================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Starting rebuild process...
echo.

echo Step 1: Stopping any running processes...
echo Checking for running SupplyLine processes...
taskkill /f /im "SupplyLine MRO Suite.exe" 2>nul
taskkill /f /im "electron.exe" 2>nul
echo Waiting for processes to close...
timeout /t 3 /nobreak >nul
echo.

echo Step 2: Cleaning old builds...
echo Attempting to remove dist folder...
if exist "dist" (
    rmdir /s /q "dist" 2>nul
    if exist "dist" (
        echo Warning: Some files in dist are still locked, continuing anyway...
    )
)

echo Attempting to remove dist-new folder...
if exist "dist-new" (
    rmdir /s /q "dist-new" 2>nul
    if exist "dist-new" (
        echo Warning: Some files in dist-new are still locked, continuing anyway...
    )
)

echo Removing frontend dist...
if exist "frontend\dist" rmdir /s /q "frontend\dist"
echo ✓ Cleanup completed (some locked files may remain)
echo.

echo Step 3: Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ✗ npm install failed!
    echo.
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo Step 4: Building frontend...
call npm run frontend:build
if %errorlevel% neq 0 (
    echo ✗ Frontend build failed!
    echo.
    pause
    exit /b 1
)
echo ✓ Frontend built
echo.

echo Step 5: Building installer...
call npm run dist:win
if %errorlevel% neq 0 (
    echo ✗ Installer build failed!
    echo.
    echo Common causes:
    echo - Antivirus blocking the build
    echo - Insufficient permissions
    echo - Missing build tools
    echo.
    echo Try running as administrator or temporarily disable antivirus.
    echo.
    pause
    exit /b 1
)
echo ✓ Installer built successfully!
echo.

echo Step 6: Checking results...
if exist "dist\SupplyLine MRO Suite Setup *.exe" (
    echo ✓ NSIS installer created
    for %%f in ("dist\SupplyLine MRO Suite Setup *.exe") do echo   File: %%f
) else (
    echo ✗ NSIS installer not found
)

if exist "dist\SupplyLine-MRO-Suite-*-portable.exe" (
    echo ✓ Portable version created
    for %%f in ("dist\SupplyLine-MRO-Suite-*-portable.exe") do echo   File: %%f
) else (
    echo ✗ Portable version not found
)

if exist "dist\win-unpacked\resources\backend\app.py" (
    echo ✓ Backend files included in build
) else (
    echo ✗ Backend files missing from build
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Uninstall the current broken version
echo 2. Install the new version from dist folder
echo 3. Test the application
echo.
echo Build output is in: %CD%\dist\
echo.
pause
