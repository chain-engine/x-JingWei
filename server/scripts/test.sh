#!/bin/bash
# 测试脚本

set -e

echo "======================================"
echo "Running tests..."
echo "======================================"

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# 运行测试
if [ "$1" == "--coverage" ] || [ "$1" == "-c" ]; then
    echo "Running tests with coverage..."
    pytest tests/ --cov=src --cov-report=html --cov-report=term
    echo "Coverage report generated in htmlcov/index.html"
else
    echo "Running tests..."
    pytest tests/ -v
fi