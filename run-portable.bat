@echo off
echo ========================================
echo SupplyLine MRO Suite - Portable Runner
echo ========================================
echo.

REM Get current directory
set CURRENT_DIR=%~dp0

REM Check if portable version exists
if exist "%CURRENT_DIR%installer\SupplyLine-MRO-Suite\SupplyLine MRO Suite.exe" (
    echo ✓ Found portable version
    echo Location: %CURRENT_DIR%installer\SupplyLine-MRO-Suite\
    echo.
    echo Starting SupplyLine MRO Suite (Portable)...
    echo.
    
    REM Change to the app directory
    cd /d "%CURRENT_DIR%installer\SupplyLine-MRO-Suite"
    
    REM Run the application
    start "" "SupplyLine MRO Suite.exe"
    
    echo Application started!
    echo If you see any errors, they should appear in a separate window.
    echo.
) else (
    echo ✗ Portable version not found!
    echo Expected location: %CURRENT_DIR%installer\SupplyLine-MRO-Suite\
    echo.
    echo Please make sure the installer folder is present.
)

pause
