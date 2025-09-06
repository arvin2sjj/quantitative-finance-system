# -*- coding: utf-8 -*-
"""
量化金融系统主程序
"""
import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.scheduler import TaskScheduler
from database import db_manager


def init_database():
    """初始化数据库"""
    try:
        print("正在初始化数据库...")
        db_manager.create_tables()
        print("数据库初始化完成")
        return True
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        return False


def run_scheduler():
    """运行定时调度器"""
    try:
        print("启动定时任务调度器...")
        scheduler = TaskScheduler()
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止调度器...")
    except Exception as e:
        print(f"调度器运行失败: {e}")


def run_once():
    """执行一次数据采集"""
    try:
        print("执行一次性数据采集...")
        scheduler = TaskScheduler()
        scheduler.run_once()
        print("数据采集完成")
    except Exception as e:
        print(f"数据采集失败: {e}")


def show_status():
    """显示系统状态"""
    try:
        from src.data_storage import DataStorage
        storage = DataStorage()
        
        print("\n=== 系统状态 ===")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"股票数量: {storage.get_stock_count()}")
        print(f"日线数据总数: {storage.get_daily_data_count()}")
        print(f"成交明细总数: {storage.get_transaction_detail_count()}")
        
        # 显示今日数据
        today = datetime.now().date()
        today_daily = storage.get_daily_data_count(today)
        today_transaction = storage.get_transaction_detail_count(today)
        print(f"今日日线数据: {today_daily}")
        print(f"今日成交明细: {today_transaction}")
        
    except Exception as e:
        print(f"获取系统状态失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='量化金融系统')
    parser.add_argument('--init', action='store_true', help='初始化数据库')
    parser.add_argument('--once', action='store_true', help='执行一次数据采集')
    parser.add_argument('--status', action='store_true', help='显示系统状态')
    parser.add_argument('--scheduler', action='store_true', help='运行定时调度器')
    
    args = parser.parse_args()
    
    # 设置日志
    Config.setup_logging()
    
    # 验证配置
    try:
        Config.validate_config()
        Config.print_config()
    except Exception as e:
        print(f"配置验证失败: {e}")
        return
    
    # 根据参数执行相应操作
    if args.init:
        if init_database():
            print("系统初始化完成！")
        else:
            print("系统初始化失败！")
    elif args.once:
        run_once()
    elif args.status:
        show_status()
    elif args.scheduler:
        run_scheduler()
    else:
        # 默认运行调度器
        print("未指定操作，默认运行定时调度器...")
        print("使用 --help 查看可用选项")
        run_scheduler()


if __name__ == "__main__":
    main()
