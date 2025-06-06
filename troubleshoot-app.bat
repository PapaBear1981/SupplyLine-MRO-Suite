@echo off
echo ========================================
echo SupplyLine MRO Suite - Troubleshooter
echo ========================================
echo.

echo Checking installation locations...
echo.

REM Check Program Files
if exist "C:\Program Files\SupplyLine MRO Suite\SupplyLine MRO Suite.exe" (
    echo ✓ Found in Program Files: C:\Program Files\SupplyLine MRO Suite\
    set APP_PATH=C:\Program Files\SupplyLine MRO Suite
    goto :found
)

REM Check Program Files (x86)
if exist "C:\Program Files (x86)\SupplyLine MRO Suite\SupplyLine MRO Suite.exe" (
    echo ✓ Found in Program Files (x86): C:\Program Files (x86)\SupplyLine MRO Suite\
    set APP_PATH=C:\Program Files (x86)\SupplyLine MRO Suite
    goto :found
)

REM Check Local AppData
if exist "%LOCALAPPDATA%\SupplyLine MRO Suite\SupplyLine MRO Suite.exe" (
    echo ✓ Found in Local AppData: %LOCALAPPDATA%\SupplyLine MRO Suite\
    set APP_PATH=%LOCALAPPDATA%\SupplyLine MRO Suite
    goto :found
)

REM Check portable location
set CURRENT_DIR=%~dp0
if exist "%CURRENT_DIR%installer\SupplyLine-MRO-Suite\SupplyLine MRO Suite.exe" (
    echo ✓ Found portable version: %CURRENT_DIR%installer\SupplyLine-MRO-Suite\
    set APP_PATH=%CURRENT_DIR%installer\SupplyLine-MRO-Suite
    goto :found
)

echo ✗ Application not found in any expected location!
echo.
echo Please check these locations manually:
echo - C:\Program Files\SupplyLine MRO Suite\
echo - C:\Program Files (x86)\SupplyLine MRO Suite\
echo - %LOCALAPPDATA%\SupplyLine MRO Suite\
echo - %CURRENT_DIR%installer\SupplyLine-MRO-Suite\
pause
exit /b 1

:found
echo.
echo Application found at: %APP_PATH%
echo.

echo Checking application files...
echo.

REM Check main executable
if exist "%APP_PATH%\SupplyLine MRO Suite.exe" (
    echo ✓ Main executable found
) else (
    echo ✗ Main executable missing!
)

REM Check resources
if exist "%APP_PATH%\resources" (
    echo ✓ Resources folder found
    if exist "%APP_PATH%\resources\app.asar" (
        echo ✓ App package found
    ) else (
        echo ✗ App package missing!
    )
) else (
    echo ✗ Resources folder missing!
)

REM Check backend files
if exist "%APP_PATH%\resources\backend" (
    echo ✓ Backend folder found
    if exist "%APP_PATH%\resources\backend\app.py" (
        echo ✓ Backend main file found
    ) else (
        echo ✗ Backend main file missing!
    )
) else (
    echo ✗ Backend folder missing!
)

echo.
echo Checking system requirements...
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python is available
    python --version
) else (
    echo ✗ Python not found in PATH
    echo This might cause backend issues
)

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Node.js is available
    node --version
) else (
    echo ✗ Node.js not found in PATH
    echo This might cause issues
)

echo.
echo Attempting to run the application with debug info...
echo.

REM Try to run the app and capture any console output
echo Starting application...
echo If you see the error again, please note the exact error message.
echo.

cd /d "%APP_PATH%"
echo Current directory: %CD%
echo.

REM Run with console output visible
"%APP_PATH%\SupplyLine MRO Suite.exe" --enable-logging --log-level=info

echo.
echo Application closed. Check above for any error messages.
echo.
pause
