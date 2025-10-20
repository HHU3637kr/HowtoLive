# PowerShell script to start Qdrant Docker container
# Data will be persisted to ./backend/.ltm_storage_qdrant

Write-Host "🚀 Starting Qdrant Docker container..." -ForegroundColor Green

# Create storage directory
$storagePath = "D:\work\worknote\project\HowtoLive\backend\.ltm_storage_qdrant"
if (-not (Test-Path $storagePath)) {
    New-Item -ItemType Directory -Path $storagePath | Out-Null
    Write-Host "✅ Created storage directory: $storagePath" -ForegroundColor Green
}

# Check if container already exists
$containerName = "qdrant_howtolive"
$existingContainer = docker ps -a --filter "name=$containerName" --format "{{.Names}}"

if ($existingContainer -eq $containerName) {
    Write-Host "⚠️  Container '$containerName' already exists. Stopping and removing..." -ForegroundColor Yellow
    docker stop $containerName | Out-Null
    docker rm $containerName | Out-Null
}

# Pull latest image
Write-Host "📦 Pulling Qdrant image..." -ForegroundColor Cyan
docker pull qdrant/qdrant

# Run container
Write-Host "🔧 Starting Qdrant container..." -ForegroundColor Cyan
docker run -d `
    --name $containerName `
    -p 6333:6333 `
    -p 6334:6334 `
    -v "${storagePath}:/qdrant/storage" `
    qdrant/qdrant

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Qdrant is running!" -ForegroundColor Green
    Write-Host "   - REST API: http://localhost:6333" -ForegroundColor Cyan
    Write-Host "   - gRPC API: localhost:6334" -ForegroundColor Cyan
    Write-Host "   - Storage: $storagePath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Check status: docker ps | findstr qdrant" -ForegroundColor Yellow
    Write-Host "🛑 Stop: docker stop $containerName" -ForegroundColor Yellow
    Write-Host "🗑️  Remove: docker rm $containerName" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Failed to start Qdrant container" -ForegroundColor Red
    Write-Host "   Please ensure Docker Desktop is running" -ForegroundColor Red
}

