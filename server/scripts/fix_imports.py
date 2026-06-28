#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复导入路径脚本"""

from pathlib import Path

def fix_file(file_path: Path):
    """修复单个文件"""
    content = file_path.read_text(encoding='utf-8')
    original = content

    # 计算相对深度
    parts = file_path.parts
    try:
        src_index = parts.index('src')
    except ValueError:
        return 0

    depth = len(parts) - src_index - 1

    if depth == 1:  # src/ 目录下
        new_content = content.replace('from ', 'from ')
    elif depth == 2:  # src/api/, src/core/ 等
        new_content = content.replace('from ', 'from ..')
    elif depth == 3:  # src/api/v1/ 等
        new_content = content.replace('from ', 'from ...')
    else:
        new_content = content

    if new_content != original:
        file_path.write_text(new_content, encoding='utf-8')
        print(f"Fixed: {file_path}")
        return 1
    return 0

# 处理所有文件
src_dir = Path('src')
for py_file in src_dir.rglob('*.py'):
    try:
        fix_file(py_file)
    except Exception as e:
        print(f"Error: {py_file} - {e}")