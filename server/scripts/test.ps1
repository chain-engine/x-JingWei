# 测试脚本 (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Running tests..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# 设置环境变量
$env:PYTHONPATH = "$env:PYTHONPATH;$(Get-Location)\src"

# 运行测试
if ($args -contains "--coverage" -or $args -contains "-c") {
    Write-Host "Running tests with coverage..." -ForegroundColor Green
    pytest tests/ --cov=src --cov-report=html --cov-report=term
    Write-Host "Coverage report generated in htmlcov\index.html" -ForegroundColor Green
} else {
    Write-Host "Running tests..." -ForegroundColor Green
    pytest tests/ -v
}