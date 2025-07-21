#!/usr/bin/env python3
"""
环境变量加载器 - 从.env文件加载阿里云凭证
"""
import os
import sys
from pathlib import Path

def load_env_file():
    """从.env文件加载环境变量到当前进程"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# 在导入时自动加载环境变量
load_env_file()
