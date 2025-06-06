@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SupplyLine MRO Suite - Truly Portable Build
echo ========================================
echo.

REM Check if we have the basic portable app
if not exist "SupplyLine-MRO-Suite-Portable-Clean" (
    echo ERROR: Base portable app not found!
    echo Please run the portable build process first.
    pause
    exit /b 1
)

echo Creating truly portable version with embedded Python...
echo.

REM Create the truly portable directory
set PORTABLE_DIR=SupplyLine-MRO-Suite-Truly-Portable
if exist "%PORTABLE_DIR%" (
    echo Removing existing truly portable build...
    rmdir /s /q "%PORTABLE_DIR%" 2>nul
)

mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\App"
mkdir "%PORTABLE_DIR%\Python"
mkdir "%PORTABLE_DIR%\Backend"

echo Step 1: Copying base Electron app...
robocopy "SupplyLine-MRO-Suite-Portable-Clean\App" "%PORTABLE_DIR%\App" /E /R:3 /W:1

echo.
echo Step 2: Downloading portable Python...
echo This will download Python 3.11 embeddable package (~25MB)

REM Download Python embeddable package
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-embed.zip'}"

if not exist "python-embed.zip" (
    echo ERROR: Failed to download Python embeddable package!
    echo Please check your internet connection and try again.
    pause
    exit /b 1
)

echo Extracting Python...
powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath '%PORTABLE_DIR%\Python' -Force"

echo.
echo Step 3: Setting up Python environment...

REM Fix the pth file to enable proper module loading
(
echo python311.zip
echo .
echo Lib
echo Lib\site-packages
echo import site
) > "%PORTABLE_DIR%\Python\python311._pth"

REM Create sitecustomize.py for additional path setup
(
echo import sys
echo import os
echo # Add current directory and site-packages to path
echo base_dir = os.path.dirname(os.path.abspath(__file__))
echo sys.path.insert(0, os.path.join(base_dir, 'Lib'))
echo sys.path.insert(0, os.path.join(base_dir, 'Lib', 'site-packages'))
) > "%PORTABLE_DIR%\Python\sitecustomize.py"

echo.
echo Step 4: Installing pip...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"

REM Create Lib and site-packages directories if they don't exist
if not exist "%PORTABLE_DIR%\Python\Lib" mkdir "%PORTABLE_DIR%\Python\Lib"
if not exist "%PORTABLE_DIR%\Python\Lib\site-packages" mkdir "%PORTABLE_DIR%\Python\Lib\site-packages"

REM Install pip
"%PORTABLE_DIR%\Python\python.exe" get-pip.py --target "%PORTABLE_DIR%\Python\Lib\site-packages" --no-warn-script-location

echo.
echo Step 5: Installing Python dependencies...
REM Copy backend to temp location for dependency installation
robocopy "backend" "%PORTABLE_DIR%\Backend" /E /R:3 /W:1

REM Install dependencies one by one for better error handling
echo Installing Flask...
"%PORTABLE_DIR%\Python\python.exe" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" --no-warn-script-location flask

echo Installing Flask-CORS...
"%PORTABLE_DIR%\Python\python.exe" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" --no-warn-script-location flask-cors

echo Installing Flask-SQLAlchemy...
"%PORTABLE_DIR%\Python\python.exe" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" --no-warn-script-location flask-sqlalchemy

echo Installing bcrypt...
"%PORTABLE_DIR%\Python\python.exe" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" --no-warn-script-location bcrypt

echo Installing python-dotenv...
"%PORTABLE_DIR%\Python\python.exe" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" --no-warn-script-location python-dotenv

echo Installing requests...
"%PORTABLE_DIR%\Python\python.exe" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" --no-warn-script-location requests

echo.
echo Step 6: Creating launcher scripts...

REM Create the main launcher
(
echo @echo off
echo setlocal
echo.
echo echo ========================================
echo echo SupplyLine MRO Suite - Truly Portable
echo echo ========================================
echo echo.
echo echo Starting SupplyLine MRO Suite...
echo echo This version includes everything needed to run!
echo echo.
echo.
echo REM Set paths
echo set SCRIPT_DIR=%%~dp0
echo set PYTHON_DIR=%%SCRIPT_DIR%%Python
echo set BACKEND_DIR=%%SCRIPT_DIR%%Backend
echo set APP_DIR=%%SCRIPT_DIR%%App
echo.
echo REM Start backend server
echo echo Starting backend server...
echo start /B "SupplyLine Backend" "%%PYTHON_DIR%%\python.exe" "%%BACKEND_DIR%%\app.py"
echo.
echo REM Wait a moment for backend to start
echo timeout /t 3 /nobreak ^>nul
echo.
echo REM Start Electron app
echo echo Starting application...
echo cd /d "%%APP_DIR%%"
echo start "" "SupplyLine MRO Suite.exe"
echo.
echo echo Application launched!
echo echo.
echo echo Default login: ADMIN001 / admin123
echo echo.
echo echo Backend server is running in the background.
echo echo Close this window to stop the backend server.
echo echo.
echo pause
echo.
echo REM Kill backend when done
echo taskkill /f /im python.exe 2^>nul
) > "%PORTABLE_DIR%\Launch-SupplyLine-Truly-Portable.bat"

REM Create a simple launcher without console
(
echo @echo off
echo setlocal
echo.
echo REM Set paths
echo set SCRIPT_DIR=%%~dp0
echo set PYTHON_DIR=%%SCRIPT_DIR%%Python
echo set BACKEND_DIR=%%SCRIPT_DIR%%Backend
echo set APP_DIR=%%SCRIPT_DIR%%App
echo.
echo REM Start backend server silently
echo start /B "SupplyLine Backend" "%%PYTHON_DIR%%\python.exe" "%%BACKEND_DIR%%\app.py"
echo.
echo REM Wait for backend to start
echo timeout /t 3 /nobreak ^>nul
echo.
echo REM Start Electron app
echo cd /d "%%APP_DIR%%"
echo start "" "SupplyLine MRO Suite.exe"
echo.
echo REM Exit this script
echo exit
) > "%PORTABLE_DIR%\Launch-SupplyLine-Silent.bat"

echo.
echo Step 7: Creating documentation...

REM Create comprehensive README
(
echo ========================================
echo SupplyLine MRO Suite - Truly Portable
echo ========================================
echo.
echo Version: 3.5.4
echo Build Date: June 2025
echo.
echo WHAT'S INCLUDED:
echo This portable version includes EVERYTHING needed to run:
echo - Python 3.11 runtime
echo - All Python dependencies
echo - Complete Electron application
echo - SQLite database
echo - No installation required!
echo.
echo QUICK START:
echo 1. Double-click "Launch-SupplyLine-Truly-Portable.bat"
echo 2. Wait for the application to start
echo 3. Login with: ADMIN001 / admin123
echo.
echo SILENT START:
echo - Use "Launch-SupplyLine-Silent.bat" for background startup
echo.
echo SYSTEM REQUIREMENTS:
echo - Windows 10 or later (64-bit)
echo - 4GB RAM minimum
echo - 500MB free disk space
echo - NO other software required!
echo.
echo FEATURES:
echo - Complete MRO management system
echo - Tool checkout/return tracking
echo - Chemical inventory management
echo - User management and RBAC
echo - Reporting and analytics
echo - Offline operation
echo - Embedded Python runtime
echo.
echo FOLDER STRUCTURE:
echo - App\                 (Electron application)
echo - Python\              (Embedded Python 3.11)
echo - Backend\              (Flask backend server)
echo - Launch scripts       (Startup files)
echo.
echo TROUBLESHOOTING:
echo - If app doesn't start, try running as Administrator
echo - Check Windows Defender isn't blocking the files
echo - Ensure you have write permissions to the folder
echo - Backend runs on port 5000 (must be available)
echo.
echo TECHNICAL DETAILS:
echo - Python: 3.11.9 Embedded
echo - Backend: Flask with SQLite
echo - Frontend: React with Bootstrap
echo - Desktop: Electron 32.3.3
echo - Database: SQLite (portable)
echo.
echo No installation required!
echo Runs completely from USB/folder.
echo.
) > "%PORTABLE_DIR%\README-Truly-Portable.txt"

echo.
echo Step 8: Cleaning up temporary files...
del python-embed.zip 2>nul
del get-pip.py 2>nul

echo.
echo ========================================
echo Truly Portable Build Complete!
echo ========================================
echo.
echo Created: %PORTABLE_DIR%
echo Total size: ~300MB (includes Python runtime)
echo.
echo Files created:
echo   - Launch-SupplyLine-Truly-Portable.bat (Main launcher)
echo   - Launch-SupplyLine-Silent.bat         (Silent launcher)
echo   - README-Truly-Portable.txt            (Documentation)
echo   - App\                                  (Electron app)
echo   - Python\                               (Python 3.11 runtime)
echo   - Backend\                              (Flask backend)
echo.
echo This version requires NO installation on target computers!
echo Just copy the folder and run the launcher.
echo.
pause
