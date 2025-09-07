#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入总结报告
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import DatabaseManager
from sqlalchemy import text
from datetime import datetime

def generate_import_summary():
    """生成数据导入总结报告"""
    print("=" * 80)
    print("深圳交易所和上海交易所股票历史数据导入总结报告")
    print("=" * 80)
    print(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 初始化数据库连接
    db_manager = DatabaseManager()
    
    with db_manager.get_session() as session:
        # 总体统计
        result = session.execute(text('''
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT symbol) as unique_stocks,
                MIN(trade_date) as earliest_date,
                MAX(trade_date) as latest_date
            FROM stock_daily_data
        '''))
        
        stats = result.fetchone()
        print("📊 总体数据统计")
        print("-" * 40)
        print(f"总记录数: {stats[0]:,} 条")
        print(f"唯一股票数: {stats[1]:,} 只")
        print(f"数据时间跨度: {stats[2]} 至 {stats[3]}")
        print(f"数据覆盖天数: {(datetime.strptime(str(stats[3]), '%Y-%m-%d') - datetime.strptime(str(stats[2]), '%Y-%m-%d')).days + 1} 天")
        print()
        
        # 按交易所统计
        result = session.execute(text('''
            SELECT 
                s.market,
                COUNT(*) as record_count,
                COUNT(DISTINCT d.symbol) as stock_count,
                MIN(d.trade_date) as earliest_date,
                MAX(d.trade_date) as latest_date
            FROM stock_daily_data d
            JOIN stock_info s ON d.symbol = s.symbol
            GROUP BY s.market
            ORDER BY s.market
        '''))
        
        market_stats = result.fetchall()
        print("🏢 按交易所统计")
        print("-" * 40)
        for row in market_stats:
            exchange_name = '上海证券交易所' if row[0] == 'SH' else '深圳证券交易所'
            print(f"{exchange_name}:")
            print(f"  - 股票数量: {row[2]:,} 只")
            print(f"  - 记录数量: {row[1]:,} 条")
            print(f"  - 时间范围: {row[3]} 至 {row[4]}")
            print()
        
        # 按年份统计
        result = session.execute(text('''
            SELECT 
                YEAR(trade_date) as year,
                COUNT(*) as record_count,
                COUNT(DISTINCT symbol) as stock_count
            FROM stock_daily_data
            GROUP BY YEAR(trade_date)
            ORDER BY year DESC
            LIMIT 10
        '''))
        
        yearly_stats = result.fetchall()
        print("📅 最近10年数据统计")
        print("-" * 40)
        for row in yearly_stats:
            print(f"{row[0]}年: {row[1]:,} 条记录, {row[2]} 只股票")
        print()
        
        # 数据质量统计
        result = session.execute(text('''
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN open_price > 0 THEN 1 END) as valid_open,
                COUNT(CASE WHEN high_price > 0 THEN 1 END) as valid_high,
                COUNT(CASE WHEN low_price > 0 THEN 1 END) as valid_low,
                COUNT(CASE WHEN close_price > 0 THEN 1 END) as valid_close,
                COUNT(CASE WHEN volume > 0 THEN 1 END) as valid_volume
            FROM stock_daily_data
        '''))
        
        quality_stats = result.fetchone()
        print("✅ 数据质量统计")
        print("-" * 40)
        print(f"总记录数: {quality_stats[0]:,}")
        print(f"有效开盘价: {quality_stats[1]:,} ({quality_stats[1]/quality_stats[0]*100:.2f}%)")
        print(f"有效最高价: {quality_stats[2]:,} ({quality_stats[2]/quality_stats[0]*100:.2f}%)")
        print(f"有效最低价: {quality_stats[3]:,} ({quality_stats[3]/quality_stats[0]*100:.2f}%)")
        print(f"有效收盘价: {quality_stats[4]:,} ({quality_stats[4]/quality_stats[0]*100:.2f}%)")
        print(f"有效成交量: {quality_stats[5]:,} ({quality_stats[5]/quality_stats[0]*100:.2f}%)")
        print()
        
        # 股票代码分布
        result = session.execute(text('''
            SELECT 
                CASE 
                    WHEN symbol LIKE '60%' THEN '上海主板'
                    WHEN symbol LIKE '68%' THEN '上海科创板'
                    WHEN symbol LIKE '00%' THEN '深圳主板'
                    WHEN symbol LIKE '30%' THEN '深圳创业板'
                    WHEN symbol LIKE '87%' OR symbol LIKE '83%' THEN '北京交易所'
                    ELSE '其他'
                END as market_type,
                COUNT(DISTINCT symbol) as stock_count,
                COUNT(*) as record_count
            FROM stock_daily_data d
            JOIN stock_info s ON d.symbol = s.symbol
            GROUP BY 
                CASE 
                    WHEN symbol LIKE '60%' THEN '上海主板'
                    WHEN symbol LIKE '68%' THEN '上海科创板'
                    WHEN symbol LIKE '00%' THEN '深圳主板'
                    WHEN symbol LIKE '30%' THEN '深圳创业板'
                    WHEN symbol LIKE '87%' OR symbol LIKE '83%' THEN '北京交易所'
                    ELSE '其他'
                END
            ORDER BY stock_count DESC
        '''))
        
        market_type_stats = result.fetchall()
        print("📈 按市场类型统计")
        print("-" * 40)
        for row in market_type_stats:
            print(f"{row[0]}: {row[1]} 只股票, {row[2]:,} 条记录")
        print()
        
        # 数据导入完成度
        result = session.execute(text('''
            SELECT 
                s.market,
                COUNT(DISTINCT d.symbol) as imported_stocks,
                (SELECT COUNT(*) FROM stock_info WHERE market = s.market) as total_stocks
            FROM stock_daily_data d
            JOIN stock_info s ON d.symbol = s.symbol
            GROUP BY s.market
        '''))
        
        completion_stats = result.fetchall()
        print("🎯 数据导入完成度")
        print("-" * 40)
        for row in completion_stats:
            exchange_name = '上海证券交易所' if row[0] == 'SH' else '深圳证券交易所'
            completion_rate = row[1] / row[2] * 100 if row[2] > 0 else 0
            print(f"{exchange_name}: {row[1]}/{row[2]} ({completion_rate:.1f}%)")
        print()
        
        print("=" * 80)
        print("数据导入总结完成")
        print("=" * 80)

if __name__ == "__main__":
    generate_import_summary()
