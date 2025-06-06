@echo off
echo ========================================
echo SupplyLine MRO Suite - Force Rebuild
echo ========================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Step 1: Force stopping ALL related processes...
echo ========================================

REM Kill all possible related processes
taskkill /f /im "SupplyLine MRO Suite.exe" 2>nul
taskkill /f /im "electron.exe" 2>nul
taskkill /f /im "node.exe" 2>nul
taskkill /f /im "npm.exe" 2>nul
taskkill /f /im "app-builder.exe" 2>nul

echo Waiting for processes to fully terminate...
timeout /t 5 /nobreak >nul

REM Check for any remaining processes using the files
echo Checking for processes using dist files...
handle.exe "dist\win-unpacked" 2>nul | findstr /i "pid" && echo Found processes using dist files

echo.

echo Step 2: Force cleaning locked files...
echo ========================================

REM Use more aggressive cleanup
echo Removing dist folder with force...
if exist "dist" (
    attrib -r -h -s "dist\*.*" /s /d 2>nul
    rd /s /q "dist" 2>nul
    if exist "dist" (
        echo Some files still locked, trying alternative method...
        REM Try to delete specific locked files
        del /f /q "dist\win-unpacked\resources\app.asar" 2>nul
        del /f /q "dist\win-unpacked\resources\*.asar" 2>nul
        rd /s /q "dist" 2>nul
    )
)

echo Removing dist-new folder with force...
if exist "dist-new" (
    attrib -r -h -s "dist-new\*.*" /s /d 2>nul
    rd /s /q "dist-new" 2>nul
)

echo Removing frontend dist...
if exist "frontend\dist" (
    rd /s /q "frontend\dist" 2>nul
)

echo Cleaning node_modules cache...
if exist "node_modules\.cache" (
    rd /s /q "node_modules\.cache" 2>nul
)

echo ✓ Aggressive cleanup completed
echo.

echo Step 3: Rebuilding node_modules (fresh start)...
echo ========================================

echo Removing node_modules...
if exist "node_modules" (
    rd /s /q "node_modules" 2>nul
)

echo Removing package-lock.json...
if exist "package-lock.json" (
    del /f /q "package-lock.json"
)

echo Installing dependencies from scratch...
call npm install
if %errorlevel% neq 0 (
    echo ✗ npm install failed!
    echo.
    pause
    exit /b 1
)
echo ✓ Dependencies installed fresh
echo.

echo Step 4: Building frontend...
echo ========================================

call npm run frontend:build
if %errorlevel% neq 0 (
    echo ✗ Frontend build failed!
    echo.
    pause
    exit /b 1
)
echo ✓ Frontend built
echo.

echo Step 5: Building installer (with retry)...
echo ========================================

echo Attempt 1: Building installer...
call npm run dist:win
if %errorlevel% equ 0 (
    echo ✓ Installer built successfully on first attempt!
    goto :check_results
)

echo First attempt failed, waiting and retrying...
timeout /t 10 /nobreak >nul

echo Attempt 2: Building installer...
call npm run dist:win
if %errorlevel% equ 0 (
    echo ✓ Installer built successfully on second attempt!
    goto :check_results
)

echo Second attempt failed, trying one more time...
timeout /t 15 /nobreak >nul

echo Attempt 3: Building installer...
call npm run dist:win
if %errorlevel% equ 0 (
    echo ✓ Installer built successfully on third attempt!
    goto :check_results
)

echo ✗ All build attempts failed!
echo.
echo This might be due to:
echo - Antivirus software blocking the build
echo - Windows Defender real-time protection
echo - Insufficient system resources
echo - Corrupted build tools
echo.
echo Try:
echo 1. Temporarily disable antivirus/Windows Defender
echo 2. Close all other applications
echo 3. Restart computer and try again
echo 4. Run as administrator
echo.
pause
exit /b 1

:check_results
echo.
echo Step 6: Verifying build results...
echo ========================================

if exist "dist\SupplyLine MRO Suite Setup *.exe" (
    echo ✓ NSIS installer created
    for %%f in ("dist\SupplyLine MRO Suite Setup *.exe") do (
        echo   File: %%f
        echo   Size: %%~zf bytes
    )
) else (
    echo ✗ NSIS installer not found
)

if exist "dist\SupplyLine-MRO-Suite-*-portable.exe" (
    echo ✓ Portable version created
    for %%f in ("dist\SupplyLine-MRO-Suite-*-portable.exe") do (
        echo   File: %%f
        echo   Size: %%~zf bytes
    )
) else (
    echo ✗ Portable version not found
)

if exist "dist\win-unpacked\resources\backend\app.py" (
    echo ✓ Backend files included in build
    echo   Backend location: dist\win-unpacked\resources\backend\
) else (
    echo ✗ Backend files missing from build
    echo   This is the original problem - backend not included!
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo The new installer should now include ALL necessary files.
echo.
echo Next steps:
echo 1. Uninstall the current broken version
echo 2. Install the new version from dist folder
echo 3. Test the application
echo.
echo Build output location: %CD%\dist\
echo.
pause
