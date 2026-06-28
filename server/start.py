#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""项目启动脚本"""

import sys
import os
from pathlib import Path

# 添加src到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )