#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量导入深圳交易所股票历史日线数据
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_fetcher import StockDataFetcher
from src.data_storage import DataStorage
from database.connection import DatabaseManager
from loguru import logger
import pandas as pd
from datetime import datetime, timedelta
import time

def import_sz_stocks_historical_data(start_date='20200101', end_date=None, batch_size=50):
    """
    批量导入深圳交易所股票历史日线数据
    
    Args:
        start_date: 开始日期，格式：YYYYMMDD
        end_date: 结束日期，格式：YYYYMMDD，默认为昨天
        batch_size: 每批处理的股票数量
    """
    if not end_date:
        end_date = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    logger.info(f"开始导入深圳交易所股票历史日线数据")
    logger.info(f"日期范围: {start_date} - {end_date}")
    logger.info(f"批次大小: {batch_size}")
    
    # 初始化组件
    db_manager = DatabaseManager()
    data_fetcher = StockDataFetcher()
    data_storage = DataStorage()
    
    try:
        # 获取股票列表
        logger.info("正在获取股票列表...")
        stock_list = data_fetcher.get_stock_list()
        
        # 筛选深圳交易所股票
        sz_stocks = stock_list[stock_list['market'] == 'SZ']
        logger.info(f"深圳交易所股票数量: {len(sz_stocks)}")
        
        if len(sz_stocks) == 0:
            logger.warning("没有找到深圳交易所股票")
            return
        
        # 分批处理
        total_batches = (len(sz_stocks) + batch_size - 1) // batch_size
        logger.info(f"将分 {total_batches} 批处理")
        
        total_success = 0
        total_failed = 0
        total_daily_data = 0
        
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(sz_stocks))
            batch_stocks = sz_stocks.iloc[start_idx:end_idx]
            
            logger.info(f"处理第 {batch_idx + 1}/{total_batches} 批，股票 {start_idx + 1}-{end_idx}")
            
            batch_success = 0
            batch_failed = 0
            batch_daily_data = 0
            
            for _, stock in batch_stocks.iterrows():
                symbol = stock['symbol']
                name = stock['name']
                
                try:
                    logger.info(f"正在获取股票 {symbol} ({name}) 的日线数据...")
                    
                    # 获取日线数据
                    daily_data = data_fetcher.get_daily_data(
                        symbol=symbol,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    if not daily_data.empty:
                        # 保存到数据库
                        saved_count = data_storage.save_daily_data(daily_data)
                        batch_daily_data += saved_count
                        batch_success += 1
                        logger.info(f"股票 {symbol} 成功保存 {saved_count} 条日线数据")
                    else:
                        logger.warning(f"股票 {symbol} 没有日线数据")
                        batch_failed += 1
                    
                    # 添加延时避免请求过于频繁
                    time.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"股票 {symbol} 处理失败: {e}")
                    batch_failed += 1
            
            # 批次统计
            total_success += batch_success
            total_failed += batch_failed
            total_daily_data += batch_daily_data
            
            logger.info(f"第 {batch_idx + 1} 批完成: 成功 {batch_success}, 失败 {batch_failed}, 数据 {batch_daily_data} 条")
            
            # 批次间延时
            if batch_idx < total_batches - 1:
                logger.info("批次间休息 5 秒...")
                time.sleep(5)
        
        # 最终统计
        logger.info("=" * 60)
        logger.info("导入完成统计")
        logger.info("=" * 60)
        logger.info(f"总股票数: {len(sz_stocks)}")
        logger.info(f"成功: {total_success} 只")
        logger.info(f"失败: {total_failed} 只")
        logger.info(f"总日线数据: {total_daily_data} 条")
        logger.info(f"成功率: {total_success / len(sz_stocks) * 100:.2f}%")
        
    except Exception as e:
        logger.error(f"批量导入失败: {e}")
        raise

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量导入深圳交易所股票历史日线数据')
    parser.add_argument('--start-date', default='20200101', help='开始日期 (YYYYMMDD)')
    parser.add_argument('--end-date', help='结束日期 (YYYYMMDD)，默认为昨天')
    parser.add_argument('--batch-size', type=int, default=50, help='每批处理的股票数量')
    
    args = parser.parse_args()
    
    try:
        import_sz_stocks_historical_data(
            start_date=args.start_date,
            end_date=args.end_date,
            batch_size=args.batch_size
        )
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
