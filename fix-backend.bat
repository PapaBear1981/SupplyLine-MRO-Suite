@echo off
echo ========================================
echo SupplyLine MRO Suite - Backend Fix
echo ========================================
echo.

REM Get current directory
set CURRENT_DIR=%~dp0
set INSTALL_DIR=C:\Program Files\SupplyLine MRO Suite

echo Current directory: %CURRENT_DIR%
echo Installation directory: %INSTALL_DIR%
echo.

REM Check if we have the source backend files
if exist "%CURRENT_DIR%installer\SupplyLine-MRO-Suite\resources\backend" (
    echo ✓ Found backend source in portable version
    set SOURCE_BACKEND=%CURRENT_DIR%installer\SupplyLine-MRO-Suite\resources\backend
) else if exist "%CURRENT_DIR%dist-new\win-unpacked\resources\backend" (
    echo ✓ Found backend source in build output
    set SOURCE_BACKEND=%CURRENT_DIR%dist-new\win-unpacked\resources\backend
) else if exist "%CURRENT_DIR%backend" (
    echo ✓ Found backend source in project root
    set SOURCE_BACKEND=%CURRENT_DIR%backend
) else (
    echo ✗ Backend source not found!
    echo.
    echo Please check these locations:
    echo - %CURRENT_DIR%installer\SupplyLine-MRO-Suite\resources\backend
    echo - %CURRENT_DIR%dist-new\win-unpacked\resources\backend  
    echo - %CURRENT_DIR%backend
    pause
    exit /b 1
)

echo Source backend: %SOURCE_BACKEND%
echo.

REM Create resources directory if it doesn't exist
if not exist "%INSTALL_DIR%\resources" (
    echo Creating resources directory...
    mkdir "%INSTALL_DIR%\resources"
)

REM Copy backend files
echo Copying backend files...
echo From: %SOURCE_BACKEND%
echo To: %INSTALL_DIR%\resources\backend
echo.

xcopy "%SOURCE_BACKEND%\*" "%INSTALL_DIR%\resources\backend\" /E /I /Y /H

REM Check if copy was successful
if exist "%INSTALL_DIR%\resources\backend\app.py" (
    echo ✓ Backend files copied successfully!
    echo.
    echo Backend files now present:
    dir "%INSTALL_DIR%\resources\backend" /B
) else (
    echo ✗ Failed to copy backend files!
    echo.
    echo This might be a permissions issue. Try running as administrator.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Backend Fix Completed!
echo ========================================
echo.
echo The backend folder has been restored to the installation.
echo You should now be able to run SupplyLine MRO Suite without errors.
echo.
echo Try running the application again from:
echo 1. Desktop shortcut
echo 2. Start Menu
echo 3. Direct path: %INSTALL_DIR%\SupplyLine MRO Suite.exe
echo.
pause
