# SupplyLine MRO Suite - Local Development Startup Script
# This script starts the full application stack using Docker Compose

Write-Host "🚀 Starting SupplyLine MRO Suite..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file. Please review and update the configuration if needed." -ForegroundColor Green
}

Write-Host ""
Write-Host "🔧 Building and starting services..." -ForegroundColor Blue

# Build and start the services
docker-compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 SupplyLine MRO Suite is starting up!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Service URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend:  http://localhost" -ForegroundColor White
    Write-Host "   Backend:   http://localhost:5000" -ForegroundColor White
    Write-Host "   Database:  localhost:5432" -ForegroundColor White
    Write-Host ""
    Write-Host "🔑 Default Admin Credentials:" -ForegroundColor Cyan
    Write-Host "   Employee Number: ADMIN001" -ForegroundColor White
    Write-Host "   Password: admin123" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 To view logs: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "🛑 To stop: docker-compose down" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⏳ Services are starting up... This may take a few minutes." -ForegroundColor Blue
    Write-Host "   You can check the status with: docker-compose ps" -ForegroundColor Blue
} else {
    Write-Host ""
    Write-Host "❌ Failed to start services. Check the logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}
