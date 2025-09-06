# -*- coding: utf-8 -*-
"""
系统监控脚本
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.data_storage import DataStorage
from database import db_manager


def get_system_status():
    """获取系统状态"""
    try:
        storage = DataStorage()
        
        print("=== 系统状态报告 ===")
        print(f"报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 基本信息
        stock_count = storage.get_stock_count()
        print(f"📊 股票总数: {stock_count}")
        
        # 今日数据
        today = datetime.now().date()
        today_daily = storage.get_daily_data_count(today)
        today_transaction = storage.get_transaction_detail_count(today)
        
        print(f"📈 今日日线数据: {today_daily}")
        print(f"💹 今日成交明细: {today_transaction}")
        
        # 历史数据统计
        total_daily = storage.get_daily_data_count()
        total_transaction = storage.get_transaction_detail_count()
        
        print(f"📊 历史日线数据: {total_daily}")
        print(f"📊 历史成交明细: {total_transaction}")
        
        # 最近7天数据
        print("\n=== 最近7天数据统计 ===")
        session = db_manager.get_session()
        
        # 查询最近7天的日线数据
        seven_days_ago = today - timedelta(days=7)
        from sqlalchemy import text
        recent_daily = session.execute(text(f"""
            SELECT trade_date, COUNT(*) as count 
            FROM stock_daily_data 
            WHERE trade_date >= '{seven_days_ago}' 
            GROUP BY trade_date 
            ORDER BY trade_date DESC
        """)).fetchall()
        
        print("日线数据:")
        for row in recent_daily:
            print(f"  {row[0]}: {row[1]} 条")
        
        # 查询最近7天的成交明细
        recent_transaction = session.execute(text(f"""
            SELECT trade_date, COUNT(*) as count 
            FROM stock_transaction_detail 
            WHERE trade_date >= '{seven_days_ago}' 
            GROUP BY trade_date 
            ORDER BY trade_date DESC
        """)).fetchall()
        
        print("成交明细:")
        for row in recent_transaction:
            print(f"  {row[0]}: {row[1]} 条")
        
        session.close()
        
        # 数据质量检查
        print("\n=== 数据质量检查 ===")
        
        # 检查今日数据完整性
        if today_daily == 0:
            print("⚠️  今日没有日线数据")
        elif today_daily < stock_count * 0.8:  # 假设80%的股票有数据
            print(f"⚠️  今日日线数据不完整: {today_daily}/{stock_count}")
        else:
            print("✅ 今日日线数据正常")
        
        if today_transaction == 0:
            print("⚠️  今日没有成交明细数据")
        else:
            print("✅ 今日成交明细数据正常")
        
        # 检查最新数据时间
        latest_daily = session.execute(text("""
            SELECT MAX(trade_date) FROM stock_daily_data
        """)).fetchone()
        
        if latest_daily and latest_daily[0]:
            days_diff = (today - latest_daily[0]).days
            if days_diff > 1:
                print(f"⚠️  最新日线数据已过期 {days_diff} 天")
            else:
                print("✅ 日线数据更新及时")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 获取系统状态失败: {e}")


def get_top_stocks():
    """获取活跃股票排行"""
    try:
        print("\n=== 今日活跃股票排行 ===")
        
        session = db_manager.get_session()
        today = datetime.now().date()
        
        # 按成交量排序
        from sqlalchemy import text
        top_volume = session.execute(text(f"""
            SELECT symbol, volume, amount 
            FROM stock_daily_data 
            WHERE trade_date = '{today}' 
            ORDER BY volume DESC 
            LIMIT 10
        """)).fetchall()
        
        print("成交量排行:")
        for i, row in enumerate(top_volume, 1):
            print(f"  {i:2d}. {row[0]} - 成交量: {row[1]:,} 成交额: {row[2]:,.2f}")
        
        # 按成交额排序
        top_amount = session.execute(text(f"""
            SELECT symbol, volume, amount 
            FROM stock_daily_data 
            WHERE trade_date = '{today}' 
            ORDER BY amount DESC 
            LIMIT 10
        """)).fetchall()
        
        print("\n成交额排行:")
        for i, row in enumerate(top_amount, 1):
            print(f"  {i:2d}. {row[0]} - 成交量: {row[1]:,} 成交额: {row[2]:,.2f}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 获取活跃股票排行失败: {e}")


def get_system_logs():
    """获取系统日志"""
    try:
        print("\n=== 最近系统日志 ===")
        
        session = db_manager.get_session()
        
        # 获取最近10条错误日志
        from sqlalchemy import text
        error_logs = session.execute(text("""
            SELECT level, message, created_at 
            FROM system_log 
            WHERE level = 'ERROR' 
            ORDER BY created_at DESC 
            LIMIT 10
        """)).fetchall()
        
        if error_logs:
            print("错误日志:")
            for log in error_logs:
                print(f"  {log[2]} [{log[0]}] {log[1]}")
        else:
            print("✅ 没有错误日志")
        
        # 获取最近10条信息日志
        info_logs = session.execute(text("""
            SELECT level, message, created_at 
            FROM system_log 
            WHERE level = 'INFO' 
            ORDER BY created_at DESC 
            LIMIT 10
        """)).fetchall()
        
        if info_logs:
            print("\n信息日志:")
            for log in info_logs:
                print(f"  {log[2]} [{log[0]}] {log[1]}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 获取系统日志失败: {e}")


def main():
    """主函数"""
    try:
        # 设置日志
        Config.setup_logging()
        
        # 获取系统状态
        get_system_status()
        
        # 获取活跃股票排行
        get_top_stocks()
        
        # 获取系统日志
        get_system_logs()
        
        print("\n=== 监控完成 ===")
        
    except Exception as e:
        print(f"❌ 监控脚本执行失败: {e}")
    finally:
        db_manager.close()


if __name__ == "__main__":
    main()
