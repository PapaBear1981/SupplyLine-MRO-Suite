# Safe Update Script for SupplyLine MRO Suite (PowerShell)
# This script updates the application while preserving the database

$ErrorActionPreference = "Stop"

# Configuration
$BackupDir = ".\database\backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupName = "pre_update_$Timestamp.db"

# Colors
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║     SupplyLine MRO Suite - Safe Update Script             ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Success "Docker is running"
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Error "docker-compose.yml not found. Please run this script from the project root."
    exit 1
}

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir | Out-Null
}

# Step 1: Create a backup of the database
Write-Status "Creating database backup..."

if (Test-Path ".\database\tools.db") {
    Copy-Item ".\database\tools.db" "$BackupDir\$BackupName"
    Write-Success "Database backed up to: $BackupDir\$BackupName"
} else {
    Write-Warning "Database file not found at .\database\tools.db"
    Write-Warning "This might be a fresh installation or database is in Docker volume"
}

# Step 2: Pull latest changes (if in git repo)
if (Test-Path ".git") {
    Write-Status "Pulling latest changes from git..."
    try {
        git pull
    } catch {
        Write-Warning "Git pull failed or no changes to pull"
    }
}

# Step 3: Build new images
Write-Status "Building new Docker images..."
docker-compose build --no-cache

# Step 4: Stop containers (but keep volumes!)
Write-Status "Stopping containers (preserving volumes)..."
docker-compose stop

# Step 5: Start updated containers
Write-Status "Starting updated containers..."
docker-compose up -d

# Step 6: Wait for services to be healthy
Write-Status "Waiting for services to start..."
Start-Sleep -Seconds 5

# Check backend health
Write-Status "Checking backend health..."
$backendHealthy = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend is healthy"
            $backendHealthy = $true
            break
        }
    } catch {
        # Continue trying
    }
    Start-Sleep -Seconds 2
}

if (-not $backendHealthy) {
    Write-Error "Backend health check failed after 30 attempts"
    Write-Warning "Check logs with: docker-compose logs backend"
    exit 1
}

# Check frontend health
Write-Status "Checking frontend health..."
$frontendHealthy = $false
for ($i = 1; $i -le 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:80" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            Write-Success "Frontend is healthy"
            $frontendHealthy = $true
            break
        }
    } catch {
        # Continue trying
    }
    Start-Sleep -Seconds 2
}

if (-not $frontendHealthy) {
    Write-Error "Frontend health check failed after 30 attempts"
    Write-Warning "Check logs with: docker-compose logs frontend"
    exit 1
}

# Step 7: Clean up old images
Write-Status "Cleaning up old Docker images..."
docker image prune -f

# Step 8: Show running containers
Write-Status "Current running containers:"
docker-compose ps

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              Update completed successfully!                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Application URLs:" -ForegroundColor Blue
Write-Host "  Frontend: " -NoNewline -ForegroundColor Blue
Write-Host "http://localhost" -ForegroundColor Green
Write-Host "  Backend:  " -NoNewline -ForegroundColor Blue
Write-Host "http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Backup Location:" -ForegroundColor Blue
Write-Host "  $BackupDir\$BackupName"
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  View logs:        " -NoNewline -ForegroundColor Yellow
Write-Host "docker-compose logs -f" -ForegroundColor Blue
Write-Host "  Restart services: " -NoNewline -ForegroundColor Yellow
Write-Host "docker-compose restart" -ForegroundColor Blue
Write-Host "  Stop services:    " -NoNewline -ForegroundColor Yellow
Write-Host "docker-compose stop" -ForegroundColor Blue
Write-Host ""

