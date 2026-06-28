# 启动脚本 (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Starting X-JingWei 经纬..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# 检查Python版本
$pythonVersion = python --version 2>&1 | ForEach-Object { $_.Split(' ')[1] }
$requiredVersion = "3.11"

try {
    $versionParts = $pythonVersion.Split('.')
    $currentVersion = [version]::new($versionParts[0], $versionParts[1])
    $minVersion = [version]::new(3, 11)

    if ($currentVersion -lt $minVersion) {
        Write-Host "Error: Python 3.11 or higher is required" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: Failed to parse Python version" -ForegroundColor Red
    exit 1
}

Write-Host "Python version: $pythonVersion" -ForegroundColor Green

# 创建必要的目录
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path data | Out-Null

# 检查配置文件
if (-not (Test-Path "config\config.yaml")) {
    Write-Host "Warning: config\config.yaml not found, using default configuration" -ForegroundColor Yellow
}

# 设置环境变量
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)\src"

# 启动应用
if ($args -contains "--reload" -or $args -contains "-r") {
    Write-Host "Starting with hot reload..." -ForegroundColor Green
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
} else {
    Write-Host "Starting in production mode..." -ForegroundColor Green
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
}