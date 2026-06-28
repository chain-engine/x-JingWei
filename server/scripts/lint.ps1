# 代码检查脚本 (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Running code quality checks..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# 运行ruff检查
Write-Host "Running ruff..." -ForegroundColor Green
ruff check src/ tests/ examples/ --fix

# 运行black格式化
Write-Host "Running black..." -ForegroundColor Green
black src/ tests/ examples/

# 运行mypy类型检查
Write-Host "Running mypy..." -ForegroundColor Green
mypy src/

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Code quality checks completed!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan