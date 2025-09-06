# -*- coding: utf-8 -*-
"""
数据库初始化脚本
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_manager
from database.models import Base
from src.config import Config


def create_database():
    """创建数据库"""
    try:
        # 设置日志
        Config.setup_logging()
        
        print("正在创建数据库表...")
        db_manager.create_tables()
        print("数据库表创建成功！")
        
        # 显示创建的表
        print("\n已创建的表:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        return True
        
    except Exception as e:
        print(f"创建数据库表失败: {e}")
        return False
    finally:
        db_manager.close()


def drop_tables():
    """删除所有表"""
    try:
        print("正在删除所有表...")
        Base.metadata.drop_all(bind=db_manager.engine)
        print("所有表已删除！")
        return True
    except Exception as e:
        print(f"删除表失败: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库初始化工具')
    parser.add_argument('--create', action='store_true', help='创建数据库表')
    parser.add_argument('--drop', action='store_true', help='删除所有表')
    
    args = parser.parse_args()
    
    if args.create:
        create_database()
    elif args.drop:
        drop_tables()
    else:
        print("请指定操作: --create 或 --drop")
        print("使用 --help 查看帮助信息")
