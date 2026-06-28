#!/bin/bash
# 代码检查脚本

set -e

echo "======================================"
echo "Running code quality checks..."
echo "======================================"

# 运行ruff检查
echo "Running ruff..."
ruff check src/ tests/ examples/ --fix

# 运行black格式化
echo "Running black..."
black src/ tests/ examples/

# 运行mypy类型检查
echo "Running mypy..."
mypy src/

echo "======================================"
echo "Code quality checks completed!"
echo "======================================"