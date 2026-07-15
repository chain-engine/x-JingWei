#!/bin/bash
# 启动脚本

set -e

echo "======================================"
echo "Starting X-JingWei 经纬..."
echo "======================================"

# 检查Python版本
python_version=$(python --version 2>&1 | awk '{print $2}')
required_version="3.11"

if ! python -c "import sys; exit(0 if tuple(map(int, sys.version.split('.')[:2])) >= tuple(map(int, '$required_version'.split('.'))) else 1)"; then
    echo "Error: Python $required_version or higher is required"
    exit 1
fi

echo "Python version: $python_version"

# 创建必要的目录
mkdir -p logs data

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "Warning: config.yaml not found, using default configuration"
fi

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# 启动应用
if [ "$1" == "--reload" ] || [ "$1" == "-r" ]; then
    echo "Starting with hot reload..."
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
else
    echo "Starting in production mode..."
    python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
fi