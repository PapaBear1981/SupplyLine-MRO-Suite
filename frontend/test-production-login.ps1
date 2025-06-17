#!/usr/bin/env pwsh

Write-Host "Testing SupplyLine MRO Suite Production Login..." -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is available
try {
    $nodeVersion = node --version
    Write-Host "Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the frontend directory
if (-not (Test-Path "package.json")) {
    Write-Host "ERROR: Please run this script from the frontend directory" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Install Playwright browsers if needed
Write-Host "Checking Playwright browsers..." -ForegroundColor Yellow
npx playwright install chromium --with-deps

# Create test-results directory if it doesn't exist
if (-not (Test-Path "test-results")) {
    New-Item -ItemType Directory -Path "test-results" | Out-Null
}

# Run the production login test
Write-Host ""
Write-Host "Running production login test..." -ForegroundColor Cyan
Write-Host "Target URL: https://supplyline-frontend-production-454313121816.us-west1.run.app/login" -ForegroundColor White
Write-Host "Credentials: ADMIN001 / admin123" -ForegroundColor White
Write-Host ""

npx playwright test production-login-test.spec.js --project=chromium --headed --reporter=line

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Production login test completed successfully!" -ForegroundColor Green
    Write-Host "Check the test-results folder for screenshots." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Production login test failed." -ForegroundColor Red
    Write-Host "Check the output above for details." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
