@echo off
REM SupplyLine MRO Suite - Build Installer Script for Windows
REM This script automates the entire build process for creating installers

echo ========================================
echo SupplyLine MRO Suite - Build Installer
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

echo Step 1: Installing dependencies...
echo.
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Installing frontend dependencies...
echo.
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo Step 3: Installing backend dependencies...
echo.
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo Step 4: Building frontend...
echo.
cd frontend
call npm run build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build frontend
    pause
    exit /b 1
)
cd ..

echo.
echo Step 5: Cleaning previous build...
echo.
taskkill /F /IM electron.exe 2>nul || echo No Electron processes found
timeout /t 2 /nobreak >nul
rmdir /s /q dist 2>nul || echo Cleaning dist folder...
timeout /t 1 /nobreak >nul

echo.
echo Step 6: Building Electron application...
echo.
call npm run dist:win
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Electron application
    echo Trying alternative build method...
    echo.
    call npx electron-builder --win --config.win.target=nsis
    if %errorlevel% neq 0 (
        echo ERROR: Alternative build also failed
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Installers created in the 'dist' folder:
echo - SupplyLine MRO Suite Setup.exe (NSIS Installer)
echo - SupplyLine-MRO-Suite-portable.exe (Portable Version)
echo.
echo You can now distribute these files for easy installation.
echo.
pause
