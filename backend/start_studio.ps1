# AgentScope Studio 启动脚本
# 使用 5000 端口（避开前端的 3000 端口）

Write-Host "================================" -ForegroundColor Cyan
Write-Host "启动 AgentScope Studio" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Studio 是否已安装
$studioInstalled = npm list -g @agentscope/studio 2>&1 | Select-String "@agentscope/studio"

if (-not $studioInstalled) {
    Write-Host "❌ AgentScope Studio 未安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装 Studio:" -ForegroundColor Yellow
    Write-Host "  npm install -g @agentscope/studio" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "✓ AgentScope Studio 已安装" -ForegroundColor Green
Write-Host ""
Write-Host "启动 Studio (端口 3001)..." -ForegroundColor Yellow
Write-Host "访问地址: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止 Studio" -ForegroundColor Gray
Write-Host ""

# 启动 Studio，指定端口为 3001
$env:PORT = "3001"
as_studio

