@echo off
echo ========================================
echo SupplyLine MRO Suite - Complete Rebuild
echo ========================================
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Navigate to the script directory (which should be the project root)
cd /d "%SCRIPT_DIR%"

echo Current directory: %CD%
echo.

REM Check if we're in the right directory
echo Checking for package.json...
if exist "package.json" (
    echo ✓ Found package.json - we're in the right directory
) else (
    echo ✗ Error: package.json not found!
    echo Script directory: %SCRIPT_DIR%
    echo Current directory: %CD%
    echo.
    echo Listing current directory contents:
    dir /b
    echo.
    echo Please make sure this script is in the project root directory
    echo (the same folder that contains package.json)
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo.
echo Checking other required files...

set MISSING_FILES=0

if exist "frontend" (
    echo ✓ Frontend directory found
) else (
    echo ✗ Frontend directory missing!
    set MISSING_FILES=1
)

if exist "backend" (
    echo ✓ Backend directory found
) else (
    echo ✗ Backend directory missing!
    set MISSING_FILES=1
)

if exist "electron" (
    echo ✓ Electron directory found
) else (
    echo ✗ Electron directory missing!
    set MISSING_FILES=1
)

echo.

if %MISSING_FILES%==1 (
    echo ✗ Some required directories are missing!
    echo Cannot proceed with rebuild.
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

echo ✓ All checks passed! Starting rebuild process...
echo.
echo Press any key to continue with the rebuild...
pause
echo.

echo Step 1: Cleaning previous builds...
echo ========================================

REM Clean dist directories
if exist "dist" (
    echo Removing old dist folder...
    rmdir /s /q "dist"
)

if exist "dist-new" (
    echo Removing old dist-new folder...
    rmdir /s /q "dist-new"
)

REM Clean frontend dist
if exist "frontend\dist" (
    echo Removing old frontend dist...
    rmdir /s /q "frontend\dist"
)

REM Clean backend cache
if exist "backend\__pycache__" (
    echo Removing backend cache...
    rmdir /s /q "backend\__pycache__"
)

REM Clean node_modules cache
if exist "node_modules\.cache" (
    echo Removing node_modules cache...
    rmdir /s /q "node_modules\.cache"
)

echo ✓ Cleanup completed
echo.

echo Step 2: Installing/updating dependencies...
echo ========================================

echo Installing Node.js dependencies...
call npm install
if %errorlevel% neq 0 (
    echo ✗ npm install failed!
    pause
    exit /b 1
)

echo ✓ Dependencies installed
echo.

echo Step 3: Building frontend...
echo ========================================

echo Building frontend application...
call npm run build:frontend
if %errorlevel% neq 0 (
    echo ✗ Frontend build failed!
    pause
    exit /b 1
)

echo ✓ Frontend built successfully
echo.

echo Step 4: Verifying backend files...
echo ========================================

if not exist "backend\app.py" (
    echo ✗ Backend main file missing!
    pause
    exit /b 1
)

if not exist "backend\requirements.txt" (
    echo ✗ Backend requirements file missing!
    pause
    exit /b 1
)

echo ✓ Backend files verified
echo.

echo Step 5: Building Electron installer...
echo ========================================

echo Building Windows installer (NSIS)...
call npm run dist:win
if %errorlevel% neq 0 (
    echo ✗ Installer build failed!
    echo.
    echo This might be due to:
    echo - Missing build dependencies
    echo - Insufficient permissions
    echo - Antivirus interference
    echo.
    pause
    exit /b 1
)

echo ✓ Installer built successfully
echo.

echo Step 6: Verifying installer contents...
echo ========================================

REM Check if installer was created
if exist "dist\SupplyLine MRO Suite Setup *.exe" (
    echo ✓ NSIS installer created
    for %%f in ("dist\SupplyLine MRO Suite Setup *.exe") do echo   File: %%f
) else (
    echo ✗ NSIS installer not found!
)

REM Check if portable version was created
if exist "dist\SupplyLine-MRO-Suite-*-portable.exe" (
    echo ✓ Portable version created
    for %%f in ("dist\SupplyLine-MRO-Suite-*-portable.exe") do echo   File: %%f
) else (
    echo ✗ Portable version not found!
)

REM Check unpacked version for backend files
if exist "dist\win-unpacked\resources\backend\app.py" (
    echo ✓ Backend files included in build
) else (
    echo ✗ Backend files missing from build!
    echo This indicates a packaging problem.
)

echo.
echo ========================================
echo Build Summary
echo ========================================

echo Build output location: %CD%\dist\
echo.

if exist "dist\SupplyLine MRO Suite Setup *.exe" (
    echo ✅ NSIS Installer: Ready for installation
) else (
    echo ❌ NSIS Installer: Failed to build
)

if exist "dist\SupplyLine-MRO-Suite-*-portable.exe" (
    echo ✅ Portable Version: Ready to run
) else (
    echo ❌ Portable Version: Failed to build
)

if exist "dist\win-unpacked\resources\backend\app.py" (
    echo ✅ Backend Files: Properly included
) else (
    echo ❌ Backend Files: Missing from package
)

echo.
echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. Test the portable version first:
echo    - Extract and run the portable .exe
echo    - Verify it starts without errors
echo.
echo 2. If portable works, test the installer:
echo    - Uninstall any existing version
echo    - Run the new installer as administrator
echo    - Test the installed application
echo.
echo 3. If you still get errors:
echo    - Check the build log above for issues
echo    - Verify all backend files are included
echo    - Try running as administrator
echo.

pause
