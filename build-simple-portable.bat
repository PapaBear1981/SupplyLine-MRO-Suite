@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SupplyLine MRO Suite - Simple Portable Build
echo ========================================
echo.

REM Check if we have the base portable app
if not exist "SupplyLine-MRO-Suite-Portable-Clean" (
    echo ERROR: Base portable app not found!
    echo Please run the portable build process first.
    pause
    exit /b 1
)

echo Creating simple portable version with WinPython...
echo This will download a portable Python distribution (~100MB)
echo.

REM Create the portable directory
set PORTABLE_DIR=SupplyLine-MRO-Suite-Simple-Portable
if exist "%PORTABLE_DIR%" (
    echo Removing existing portable build...
    rmdir /s /q "%PORTABLE_DIR%" 2>nul
)

mkdir "%PORTABLE_DIR%"
mkdir "%PORTABLE_DIR%\App"
mkdir "%PORTABLE_DIR%\Python"
mkdir "%PORTABLE_DIR%\Backend"

echo Step 1: Copying base Electron app...
robocopy "SupplyLine-MRO-Suite-Portable-Clean\App" "%PORTABLE_DIR%\App" /E /R:3 /W:1

echo.
echo Step 2: Downloading WinPython (portable Python)...
echo This may take a few minutes...

REM Download WinPython portable
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/winpython/winpython/releases/download/7.1.20240315final/Winpython64-3.11.8.0dot.exe' -OutFile 'winpython.exe'}"

if not exist "winpython.exe" (
    echo ERROR: Failed to download WinPython!
    echo Trying alternative approach with standard Python...
    goto :STANDARD_PYTHON
)

echo Extracting WinPython...
winpython.exe -o"%PORTABLE_DIR%\Python" -y

REM Find the extracted Python directory
for /d %%i in ("%PORTABLE_DIR%\Python\WPy64-*") do set PYTHON_ROOT=%%i

if not exist "%PYTHON_ROOT%" (
    echo ERROR: WinPython extraction failed!
    goto :STANDARD_PYTHON
)

set PYTHON_EXE=%PYTHON_ROOT%\python-3.11.8.amd64\python.exe
goto :INSTALL_DEPS

:STANDARD_PYTHON
echo.
echo Using standard Python approach...

REM Download standard Python embeddable
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile 'python-embed.zip'}"

if not exist "python-embed.zip" (
    echo ERROR: Failed to download Python!
    echo Please check your internet connection.
    pause
    exit /b 1
)

echo Extracting Python...
powershell -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath '%PORTABLE_DIR%\Python' -Force"

REM Download get-pip.py
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PORTABLE_DIR%\Python\get-pip.py'"

REM Fix Python paths
echo python311.zip > "%PORTABLE_DIR%\Python\python311._pth"
echo . >> "%PORTABLE_DIR%\Python\python311._pth"
echo Lib >> "%PORTABLE_DIR%\Python\python311._pth"
echo Lib\site-packages >> "%PORTABLE_DIR%\Python\python311._pth"

REM Create Lib directory
mkdir "%PORTABLE_DIR%\Python\Lib"
mkdir "%PORTABLE_DIR%\Python\Lib\site-packages"

REM Install pip
"%PORTABLE_DIR%\Python\python.exe" "%PORTABLE_DIR%\Python\get-pip.py" --target "%PORTABLE_DIR%\Python\Lib\site-packages"

set PYTHON_EXE=%PORTABLE_DIR%\Python\python.exe

:INSTALL_DEPS
echo.
echo Step 3: Installing Python dependencies...
REM Copy backend files
robocopy "backend" "%PORTABLE_DIR%\Backend" /E /R:3 /W:1

REM Install dependencies
echo Installing Flask...
"%PYTHON_EXE%" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" flask

echo Installing Flask-CORS...
"%PYTHON_EXE%" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" flask-cors

echo Installing Flask-SQLAlchemy...
"%PYTHON_EXE%" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" flask-sqlalchemy

echo Installing bcrypt...
"%PYTHON_EXE%" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" bcrypt

echo Installing python-dotenv...
"%PYTHON_EXE%" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" python-dotenv

echo Installing requests...
"%PYTHON_EXE%" -m pip install --target "%PORTABLE_DIR%\Python\Lib\site-packages" requests

echo.
echo Step 4: Creating launcher scripts...

REM Create the main launcher
(
echo @echo off
echo setlocal
echo.
echo echo ========================================
echo echo SupplyLine MRO Suite - Simple Portable
echo echo ========================================
echo echo.
echo echo Starting SupplyLine MRO Suite...
echo echo This version includes everything needed to run!
echo echo.
echo.
echo REM Set paths
echo set SCRIPT_DIR=%%~dp0
echo set PYTHON_EXE=%%SCRIPT_DIR%%Python\python.exe
echo set BACKEND_DIR=%%SCRIPT_DIR%%Backend
echo set APP_DIR=%%SCRIPT_DIR%%App
echo.
echo REM Check if WinPython was used
echo if exist "%%SCRIPT_DIR%%Python\WPy64-*" (
echo     for /d %%%%i in ("%%SCRIPT_DIR%%Python\WPy64-*") do set PYTHON_ROOT=%%%%i
echo     set PYTHON_EXE=!PYTHON_ROOT!\python-3.11.8.amd64\python.exe
echo )
echo.
echo REM Start backend server
echo echo Starting backend server...
echo cd /d "%%BACKEND_DIR%%"
echo start /B "SupplyLine Backend" "%%PYTHON_EXE%%" app.py
echo.
echo REM Wait a moment for backend to start
echo timeout /t 5 /nobreak ^>nul
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
) > "%PORTABLE_DIR%\Launch-SupplyLine-Simple-Portable.bat"

echo.
echo Step 5: Creating documentation...

(
echo ========================================
echo SupplyLine MRO Suite - Simple Portable
echo ========================================
echo.
echo Version: 3.5.4
echo Build Date: June 2025
echo.
echo WHAT'S INCLUDED:
echo This portable version includes EVERYTHING needed to run:
echo - Portable Python distribution
echo - All Python dependencies
echo - Complete Electron application
echo - SQLite database
echo - No installation required!
echo.
echo QUICK START:
echo 1. Double-click "Launch-SupplyLine-Simple-Portable.bat"
echo 2. Wait for the application to start
echo 3. Login with: ADMIN001 / admin123
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
echo - Portable Python runtime
echo.
echo FOLDER STRUCTURE:
echo - App\                 (Electron application)
echo - Python\              (Portable Python)
echo - Backend\              (Flask backend server)
echo - Launch script        (Startup file)
echo.
echo TROUBLESHOOTING:
echo - If app doesn't start, try running as Administrator
echo - Check Windows Defender isn't blocking the files
echo - Ensure you have write permissions to the folder
echo - Backend runs on port 5000 (must be available)
echo.
echo TECHNICAL DETAILS:
echo - Python: 3.11.x Portable
echo - Backend: Flask with SQLite
echo - Frontend: React with Bootstrap
echo - Desktop: Electron 32.3.3
echo - Database: SQLite (portable)
echo.
echo No installation required!
echo Runs completely from folder/USB.
echo.
) > "%PORTABLE_DIR%\README-Simple-Portable.txt"

echo.
echo Step 6: Cleaning up temporary files...
del winpython.exe 2>nul
del python-embed.zip 2>nul

echo.
echo ========================================
echo Simple Portable Build Complete!
echo ========================================
echo.
echo Created: %PORTABLE_DIR%
echo Total size: ~500MB (includes portable Python)
echo.
echo Files created:
echo   - Launch-SupplyLine-Simple-Portable.bat (Main launcher)
echo   - README-Simple-Portable.txt            (Documentation)
echo   - App\                                   (Electron app)
echo   - Python\                                (Portable Python)
echo   - Backend\                               (Flask backend)
echo.
echo This version requires NO installation on target computers!
echo Just copy the folder and run the launcher.
echo.
pause
