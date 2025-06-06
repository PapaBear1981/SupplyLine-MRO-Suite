@echo off
title SupplyLine MRO Suite - Portable PWA
echo ========================================
echo  SupplyLine MRO Suite - Portable PWA
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo ✅ Node.js found
echo.

REM Install dependencies if needed
if not exist "server\node_modules" (
    echo 📦 Installing server dependencies...
    cd server
    npm install
    cd ..
    echo.
)

echo 🚀 Starting SupplyLine MRO Suite PWA Server...
echo.
npm start
pause