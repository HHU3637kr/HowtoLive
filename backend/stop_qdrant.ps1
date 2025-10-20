# PowerShell script to stop Qdrant Docker container

$containerName = "qdrant_howtolive"

Write-Host "🛑 Stopping Qdrant container: $containerName" -ForegroundColor Yellow

$existingContainer = docker ps --filter "name=$containerName" --format "{{.Names}}"

if ($existingContainer -eq $containerName) {
    docker stop $containerName
    Write-Host "✅ Container stopped" -ForegroundColor Green
} else {
    Write-Host "⚠️  Container '$containerName' is not running" -ForegroundColor Yellow
}

