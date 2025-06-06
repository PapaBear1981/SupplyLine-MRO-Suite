@echo off
echo ========================================
echo SupplyLine MRO Suite - Quick Build Test
echo ========================================
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

echo Checking icon files...
if exist "assets\icon.ico" (
    echo ✓ icon.ico found
) else (
    echo ✗ icon.ico missing!
    echo This will cause the build to fail.
    pause
    exit /b 1
)

if exist "assets\icon.png" (
    echo ✓ icon.png found
) else (
    echo ✗ icon.png missing!
)

echo.

echo Testing build with fixed icon configuration...
echo ========================================

echo Building installer (this may take 5-10 minutes)...
call npm run dist:win

if %errorlevel% equ 0 (
    echo.
    echo ✓ Build successful!
    echo.
    echo Checking results...
    
    if exist "dist\SupplyLine MRO Suite Setup *.exe" (
        echo ✓ NSIS installer created
        for %%f in ("dist\SupplyLine MRO Suite Setup *.exe") do echo   File: %%f
    )
    
    if exist "dist\SupplyLine-MRO-Suite-*-portable.exe" (
        echo ✓ Portable version created
        for %%f in ("dist\SupplyLine-MRO-Suite-*-portable.exe") do echo   File: %%f
    )
    
    if exist "dist\win-unpacked\resources\backend\app.py" (
        echo ✓ Backend files included
    ) else (
        echo ✗ Backend files still missing!
    )
    
    echo.
    echo ========================================
    echo SUCCESS! Installer built with all files
    echo ========================================
    
) else (
    echo.
    echo ✗ Build failed again.
    echo.
    echo If you're still getting icon errors, we may need to:
    echo 1. Recreate the icon.ico file
    echo 2. Use a different icon format
    echo 3. Remove icon configuration temporarily
    echo.
)

echo.
pause
