# SupplyLine MRO Suite - Local Development Stop Script
# This script stops the full application stack

Write-Host "🛑 Stopping SupplyLine MRO Suite..." -ForegroundColor Yellow
Write-Host ""

# Stop the services
docker-compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All services stopped successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 To remove all data (including database): docker-compose down -v" -ForegroundColor Blue
    Write-Host "🧹 To clean up images: docker system prune" -ForegroundColor Blue
} else {
    Write-Host ""
    Write-Host "❌ Error stopping services. You may need to stop them manually." -ForegroundColor Red
    Write-Host "   Try: docker-compose down --remove-orphans" -ForegroundColor Yellow
}
