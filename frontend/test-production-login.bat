@echo off
echo Testing SupplyLine MRO Suite Production Login...
echo.

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if we're in the frontend directory
if not exist "package.json" (
    echo ERROR: Please run this script from the frontend directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Install Playwright browsers if needed
echo Checking Playwright browsers...
npx playwright install chromium --with-deps

REM Create test-results directory if it doesn't exist
if not exist "test-results" mkdir test-results

REM Run the production login test
echo.
echo Running production login test...
echo Target URL: https://supplyline-frontend-production-454313121816.us-west1.run.app/login
echo Credentials: ADMIN001 / admin123
echo.

npx playwright test production-login-test.spec.js --project=chromium --headed --reporter=line

if %errorlevel% equ 0 (
    echo.
    echo ✅ Production login test completed successfully!
    echo Check the test-results folder for screenshots.
) else (
    echo.
    echo ❌ Production login test failed.
    echo Check the output above for details.
)

echo.
pause
