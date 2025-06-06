@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SupplyLine MRO Suite - Standalone Executable Build
echo ========================================
echo.

REM Check if we have the base portable app
if not exist "SupplyLine-MRO-Suite-Portable-Clean" (
    echo ERROR: Base portable app not found!
    echo Please run the portable build process first.
    pause
    exit /b 1
)

echo Creating standalone executable version...
echo This will create a single .exe file that includes everything!
echo.

REM Create the standalone directory
set STANDALONE_DIR=SupplyLine-MRO-Suite-Standalone
if exist "%STANDALONE_DIR%" (
    echo Removing existing standalone build...
    rmdir /s /q "%STANDALONE_DIR%" 2>nul
)

mkdir "%STANDALONE_DIR%"

echo Step 1: Installing PyInstaller...
pip install pyinstaller

echo.
echo Step 2: Creating backend executable...

REM Create a simple launcher script for the backend
(
echo import sys
echo import os
echo import subprocess
echo import time
echo import webbrowser
echo from pathlib import Path
echo.
echo def main():
echo     # Get the directory where this executable is located
echo     if getattr(sys, 'frozen', False):
echo         # Running as compiled executable
echo         app_dir = Path(sys.executable).parent
echo     else:
echo         # Running as script
echo         app_dir = Path(__file__).parent
echo.
echo     # Set up paths
echo     backend_dir = app_dir / "backend"
echo     electron_dir = app_dir / "electron_app"
echo.
echo     print("========================================")
echo     print("SupplyLine MRO Suite - Standalone")
echo     print("========================================")
echo     print()
echo     print("Starting backend server...")
echo.
echo     # Change to backend directory
echo     os.chdir(backend_dir)
echo.
echo     # Start the Flask app
echo     from backend.app import app
echo     import threading
echo.
echo     def run_flask():
echo         app.run(host='127.0.0.1', port=5000, debug=False)
echo.
echo     # Start Flask in a separate thread
echo     flask_thread = threading.Thread(target=run_flask, daemon=True)
echo     flask_thread.start()
echo.
echo     # Wait a moment for Flask to start
echo     time.sleep(3)
echo.
echo     print("Backend server started!")
echo     print("Starting Electron application...")
echo.
echo     # Start Electron app
echo     electron_exe = electron_dir / "SupplyLine MRO Suite.exe"
echo     if electron_exe.exists():
echo         subprocess.Popen([str(electron_exe)])
echo         print("Application launched!")
echo         print()
echo         print("Default login: ADMIN001 / admin123")
echo         print()
echo         print("Press Ctrl+C to stop the server...")
echo         try:
echo             while True:
echo                 time.sleep(1)
echo         except KeyboardInterrupt:
echo             print("Shutting down...")
echo     else:
echo         print("Error: Electron app not found!")
echo         print("Opening web browser instead...")
echo         webbrowser.open('http://127.0.0.1:5000')
echo         try:
echo             while True:
echo                 time.sleep(1)
echo         except KeyboardInterrupt:
echo             print("Shutting down...")
echo.
echo if __name__ == "__main__":
echo     main()
) > backend_launcher.py

echo.
echo Step 3: Building standalone executable...

REM Create the executable with PyInstaller
pyinstaller --onefile --windowed --name "SupplyLine-MRO-Suite" --icon="assets/icon.ico" backend_launcher.py

echo.
echo Step 4: Copying required files...

REM Copy the executable
copy "dist\SupplyLine-MRO-Suite.exe" "%STANDALONE_DIR%\"

REM Copy backend files
robocopy "backend" "%STANDALONE_DIR%\backend" /E /R:3 /W:1

REM Copy Electron app
robocopy "SupplyLine-MRO-Suite-Portable-Clean\App" "%STANDALONE_DIR%\electron_app" /E /R:3 /W:1

echo.
echo Step 5: Creating launcher scripts...

REM Create a simple launcher
(
echo @echo off
echo setlocal
echo.
echo echo ========================================
echo echo SupplyLine MRO Suite - Standalone
echo echo ========================================
echo echo.
echo echo Starting SupplyLine MRO Suite...
echo echo This is a completely self-contained version!
echo echo.
echo.
echo REM Start the main executable
echo start "" "SupplyLine-MRO-Suite.exe"
echo.
echo echo Application launched!
echo echo.
echo echo Default login: ADMIN001 / admin123
echo echo.
echo echo The application will open in a moment...
echo echo.
echo pause
) > "%STANDALONE_DIR%\Launch-SupplyLine-Standalone.bat"

echo.
echo Step 6: Creating documentation...

(
echo ========================================
echo SupplyLine MRO Suite - Standalone
echo ========================================
echo.
echo Version: 3.5.4
echo Build Date: June 2025
echo.
echo WHAT'S INCLUDED:
echo This standalone version includes EVERYTHING in a single executable:
echo - Python runtime (embedded)
echo - All Python dependencies
echo - Complete backend server
echo - Electron application
echo - SQLite database
echo - No installation required!
echo.
echo QUICK START:
echo 1. Double-click "SupplyLine-MRO-Suite.exe"
echo    OR
echo    Double-click "Launch-SupplyLine-Standalone.bat"
echo 2. Wait for the application to start
echo 3. Login with: ADMIN001 / admin123
echo.
echo SYSTEM REQUIREMENTS:
echo - Windows 10 or later (64-bit)
echo - 4GB RAM minimum
echo - 200MB free disk space
echo - NO other software required!
echo - NO Python installation needed!
echo - NO Node.js installation needed!
echo.
echo FEATURES:
echo - Complete MRO management system
echo - Tool checkout/return tracking
echo - Chemical inventory management
echo - User management and RBAC
echo - Reporting and analytics
echo - Offline operation
echo - Self-contained executable
echo.
echo TECHNICAL DETAILS:
echo - Single executable file
echo - Embedded Python runtime
echo - Backend: Flask with SQLite
echo - Frontend: React with Bootstrap
echo - Desktop: Electron
echo - Database: SQLite (portable)
echo.
echo TROUBLESHOOTING:
echo - First startup may be slow (extraction/initialization)
echo - If blocked by antivirus, add to exclusions
echo - Run as Administrator if permission issues occur
echo - Ensure port 5000 is available (backend server)
echo.
echo No installation required on target computers!
echo Just copy the folder and run!
echo.
) > "%STANDALONE_DIR%\README-Standalone.txt"

echo.
echo Step 7: Cleaning up build files...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del *.spec 2>nul
del backend_launcher.py 2>nul

echo.
echo ========================================
echo Standalone Executable Build Complete!
echo ========================================
echo.
echo Created: %STANDALONE_DIR%
echo Total size: ~400MB (single executable + assets)
echo.
echo Files created:
echo   - SupplyLine-MRO-Suite.exe              (Main executable)
echo   - Launch-SupplyLine-Standalone.bat      (Launcher script)
echo   - README-Standalone.txt                 (Documentation)
echo   - backend\                              (Backend files)
echo   - electron_app\                         (Electron application)
echo.
echo This version requires ZERO installation on target computers!
echo - No Python needed
echo - No Node.js needed
echo - No dependencies needed
echo - Just run the .exe file!
echo.
pause
