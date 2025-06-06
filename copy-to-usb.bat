@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SupplyLine MRO Suite - USB Deployment
echo ========================================
echo.

REM Check if portable app exists
if not exist "SupplyLine-MRO-Suite-Portable-Clean" (
    echo ERROR: Portable app directory not found!
    echo Please ensure the portable app has been built first.
    echo Looking for: SupplyLine-MRO-Suite-Portable-Clean
    echo.
    pause
    exit /b 1
)

REM List available drives
echo Available drives:
for /f "tokens=1" %%d in ('wmic logicaldisk where "drivetype=2" get deviceid /value ^| find "="') do (
    set drive=%%d
    set drive=!drive:~9!
    if defined drive (
        echo   !drive!
    )
)

echo.
set /p usb_drive="Enter USB drive letter (e.g., E): "

REM Validate drive letter
if "%usb_drive%"=="" (
    echo ERROR: No drive letter specified!
    pause
    exit /b 1
)

REM Add colon if not present
echo %usb_drive% | findstr ":" >nul
if errorlevel 1 set usb_drive=%usb_drive%:

REM Check if drive exists
if not exist "%usb_drive%\" (
    echo ERROR: Drive %usb_drive% not found or not accessible!
    pause
    exit /b 1
)

REM Check if it's actually a removable drive
for /f "tokens=2" %%a in ('wmic logicaldisk where "deviceid='%usb_drive%'" get drivetype /value ^| find "="') do (
    set drivetype=%%a
    set drivetype=!drivetype:~10!
)

if not "!drivetype!"=="2" (
    echo WARNING: %usb_drive% does not appear to be a removable drive!
    echo Drive type: !drivetype! (2=Removable, 3=Fixed)
    set /p continue="Continue anyway? (y/N): "
    if /i not "!continue!"=="y" (
        echo Operation cancelled.
        pause
        exit /b 1
    )
)

echo.
echo Copying SupplyLine MRO Suite to %usb_drive%...
echo.

REM Create destination directory
set dest_dir=%usb_drive%\SupplyLine-MRO-Suite
if exist "%dest_dir%" (
    echo Removing existing installation...
    rmdir /s /q "%dest_dir%" 2>nul
    if exist "%dest_dir%" (
        echo WARNING: Could not completely remove existing installation.
        echo Some files may be in use. Please close any running instances.
        pause
    )
)

mkdir "%dest_dir%" 2>nul

REM Copy portable app
echo Copying application files...
robocopy "SupplyLine-MRO-Suite-Portable-Clean" "%dest_dir%" /E /R:3 /W:1 /MT:4

if errorlevel 8 (
    echo ERROR: Copy operation failed!
    pause
    exit /b 1
)

REM Create autorun.inf for convenience (optional)
echo Creating autorun.inf...
(
echo [autorun]
echo label=SupplyLine MRO Suite
echo icon=SupplyLine-MRO-Suite\App\SupplyLine MRO Suite.exe
echo action=Launch SupplyLine MRO Suite
echo open=SupplyLine-MRO-Suite\Launch-SupplyLine.bat
) > "%usb_drive%\autorun.inf"

REM Create a desktop shortcut on the USB
echo Creating USB launcher...
(
echo @echo off
echo cd /d "%%~dp0SupplyLine-MRO-Suite"
echo call Launch-SupplyLine.bat
) > "%usb_drive%\Launch SupplyLine MRO Suite.bat"

REM Create a quick info file
echo Creating info file...
(
echo ========================================
echo SupplyLine MRO Suite - Portable Edition
echo ========================================
echo.
echo Version: 3.5.4
echo Build Date: June 2025
echo.
echo QUICK START:
echo 1. Double-click "Launch SupplyLine MRO Suite.bat"
echo 2. Login with: ADMIN001 / admin123
echo.
echo MANUAL START:
echo 1. Navigate to SupplyLine-MRO-Suite folder
echo 2. Double-click Launch-SupplyLine.bat
echo.
echo SYSTEM REQUIREMENTS:
echo - Windows 10 or later (64-bit)
echo - Python 3.8+ (must be in PATH)
echo - 4GB RAM minimum
echo - 500MB free disk space
echo.
echo FEATURES:
echo - Complete MRO management system
echo - Tool checkout/return tracking
echo - Chemical inventory management
echo - User management and RBAC
echo - Reporting and analytics
echo - Offline operation
echo.
echo No installation required!
echo Runs completely from USB drive.
echo.
) > "%usb_drive%\README - SupplyLine MRO Suite.txt"

echo.
echo ========================================
echo USB Deployment Complete!
echo ========================================
echo.
echo The SupplyLine MRO Suite has been copied to %usb_drive%
echo Total size: ~200MB
echo.
echo Files created on USB:
echo   - SupplyLine-MRO-Suite\          (Main application folder)
echo   - Launch SupplyLine MRO Suite.bat (Quick launcher)
echo   - README - SupplyLine MRO Suite.txt (Instructions)
echo   - autorun.inf                    (Auto-launch support)
echo.
echo To use on any computer:
echo 1. Insert the USB drive
echo 2. Double-click "Launch SupplyLine MRO Suite.bat"
echo    OR
echo    Navigate to SupplyLine-MRO-Suite folder and run Launch-SupplyLine.bat
echo.
echo Default login credentials:
echo   Username: ADMIN001
echo   Password: admin123
echo.
echo The application will run completely from the USB drive.
echo No installation required on the target computer.
echo Python 3.8+ must be installed on the target system.
echo.
pause
