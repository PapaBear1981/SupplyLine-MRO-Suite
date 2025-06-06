@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SupplyLine MRO Suite - Simple Portable USB Deployment
echo ========================================
echo.

REM Check if we have the simple portable app
if not exist "SupplyLine-MRO-Suite-Simple-Portable" (
    echo ERROR: Simple portable app not found!
    echo Please run build-simple-portable.bat first.
    pause
    exit /b 1
)

echo Available drives:
wmic logicaldisk get size,freespace,caption

echo.
set /p USB_DRIVE="Enter USB drive letter (e.g., E): "

REM Validate drive letter
if "%USB_DRIVE%"=="" (
    echo ERROR: No drive letter specified!
    pause
    exit /b 1
)

REM Check if drive exists
if not exist "%USB_DRIVE%:\" (
    echo ERROR: Drive %USB_DRIVE%: does not exist!
    pause
    exit /b 1
)

REM Check drive type (optional warning)
for /f "tokens=2" %%i in ('fsutil fsinfo drivetype %USB_DRIVE%:') do set DRIVE_TYPE=%%i
echo Drive type: %DRIVE_TYPE% (2=Removable, 3=Fixed)
if not "%DRIVE_TYPE%"=="Removable" (
    echo WARNING: %USB_DRIVE%: does not appear to be a removable drive
    set /p CONTINUE="Continue anyway? (y/N):"
    if /i not "!CONTINUE!"=="y" (
        echo Cancelled by user.
        pause
        exit /b 1
    )
)

echo.
echo Copying SupplyLine MRO Suite (Simple Portable) to %USB_DRIVE%:...
echo This includes embedded Python runtime and may take several minutes...
echo.

REM Remove existing installation
echo Removing existing installation...
if exist "%USB_DRIVE%:\SupplyLine-MRO-Suite" (
    rmdir /s /q "%USB_DRIVE%:\SupplyLine-MRO-Suite" 2>nul
    if exist "%USB_DRIVE%:\SupplyLine-MRO-Suite" (
        echo WARNING: Could not completely remove existing installation.
        echo Some files may be in use. Please close any running instances.
        pause
    )
)

REM Copy application files
echo Copying application files...
robocopy "SupplyLine-MRO-Suite-Simple-Portable" "%USB_DRIVE%:\SupplyLine-MRO-Suite" /E /R:3 /W:1

REM Create USB launcher
echo Creating USB launcher...
(
echo @echo off
echo setlocal
echo.
echo echo ========================================
echo echo SupplyLine MRO Suite - Simple Portable
echo echo ========================================
echo echo.
echo echo Starting SupplyLine MRO Suite from USB...
echo echo This version includes embedded Python runtime!
echo echo.
echo.
echo REM Get the drive letter of this USB
echo set USB_DRIVE=%%~d0
echo set APP_DIR=%%USB_DRIVE%%\SupplyLine-MRO-Suite
echo.
echo REM Check if app exists
echo if not exist "%%APP_DIR%%" (
echo     echo ERROR: SupplyLine-MRO-Suite folder not found on USB!
echo     pause
echo     exit /b 1
echo )
echo.
echo REM Navigate to app directory and run
echo cd /d "%%APP_DIR%%"
echo.
echo REM Check for launcher script
echo if exist "Launch-SupplyLine-Simple-Portable.bat" (
echo     echo Running Simple Portable launcher...
echo     call "Launch-SupplyLine-Simple-Portable.bat"
echo ) else if exist "Launch-SupplyLine.bat" (
echo     echo Running standard launcher...
echo     call "Launch-SupplyLine.bat"
echo ) else (
echo     echo ERROR: No launcher script found!
echo     echo Please check the installation.
echo     pause
echo )
) > "%USB_DRIVE%:\Launch SupplyLine MRO Suite - Simple Portable.bat"

REM Create autorun.inf
echo Creating autorun.inf...
(
echo [autorun]
echo open=Launch SupplyLine MRO Suite - Simple Portable.bat
echo icon=SupplyLine-MRO-Suite\App\SupplyLine MRO Suite.exe,0
echo label=SupplyLine MRO Suite
) > "%USB_DRIVE%:\autorun.inf"

REM Create info file
echo Creating info file...
(
echo ========================================
echo SupplyLine MRO Suite - Simple Portable
echo ========================================
echo.
echo Version: 3.5.4
echo Build Date: June 2025
echo.
echo WHAT MAKES THIS "SIMPLE PORTABLE":
echo This version includes EVERYTHING needed:
echo - Portable Python 3.11 runtime
echo - All Python dependencies pre-installed
echo - Complete Electron application
echo - SQLite database
echo - NO installation required on ANY Windows PC
echo.
echo QUICK START:
echo 1. Double-click "Launch SupplyLine MRO Suite - Simple Portable.bat"
echo 2. Wait for the application to start (may take 30-60 seconds)
echo 3. Login with: ADMIN001 / admin123
echo.
echo ALTERNATIVE START:
echo 1. Navigate to SupplyLine-MRO-Suite folder
echo 2. Double-click "Launch-SupplyLine-Simple-Portable.bat"
echo.
echo SYSTEM REQUIREMENTS:
echo - Windows 10 or later (64-bit)
echo - 4GB RAM minimum
echo - 500MB free disk space
echo - NO other software required
echo - NO Python installation needed
echo - NO Node.js installation needed
echo.
echo FEATURES:
echo - Complete MRO management system
echo - Tool checkout/return tracking
echo - Chemical inventory management
echo - User management and RBAC
echo - Reporting and analytics
echo - Offline operation
echo - Portable Python runtime
echo - Self-contained database
echo.
echo TECHNICAL DETAILS:
echo - Total size: ~500MB (includes portable Python)
echo - Python: 3.11.x Portable
echo - Backend: Flask with SQLite
echo - Frontend: React with Bootstrap
echo - Desktop: Electron 32.3.3
echo - Database: SQLite (portable)
echo.
echo TROUBLESHOOTING:
echo - First startup may be slow (Python initialization)
echo - If blocked by antivirus, add folder to exclusions
echo - Run as Administrator if permission issues occur
echo - Ensure port 5000 is available (backend server)
echo.
echo No installation required on target computers
echo Just plug in USB and run
echo.
) > "%USB_DRIVE%:\README - SupplyLine MRO Suite - Simple Portable.txt"

echo.
echo ========================================
echo Simple Portable USB Deployment Complete
echo ========================================
echo.
echo The SupplyLine MRO Suite (Simple Portable) has been copied to %USB_DRIVE%:
echo Total size: ~500MB (includes portable Python runtime)
echo.
echo Files created on USB:
echo   - SupplyLine-MRO-Suite\                                (Main application folder)
echo   - Launch SupplyLine MRO Suite - Simple Portable.bat    (USB launcher)
echo   - README - SupplyLine MRO Suite - Simple Portable.txt  (Instructions)
echo   - autorun.inf                                           (Auto-launch support)
echo.
echo To use on ANY Windows computer:
echo 1. Insert the USB drive
echo 2. Double-click "Launch SupplyLine MRO Suite - Simple Portable.bat"
echo 3. Wait for startup (may take 30-60 seconds first time)
echo 4. Login with ADMIN001 / admin123
echo.
echo This version requires ZERO installation on target computers
echo - No Python needed
echo - No Node.js needed
echo - No dependencies needed
echo - Just plug and play
echo.
echo Default login credentials:
echo   Username: ADMIN001
echo   Password: admin123
echo.
pause
