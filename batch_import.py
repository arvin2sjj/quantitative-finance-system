#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入历史数据启动脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.batch_importer import main

if __name__ == "__main__":
    main()
