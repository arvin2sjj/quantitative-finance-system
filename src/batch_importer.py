# -*- coding: utf-8 -*-
"""
批量历史数据导入模块
"""
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from loguru import logger
import time
import os
import sys
from tqdm import tqdm

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import StockDataFetcher
from src.data_storage import DataStorage


class BatchImporter:
    """批量数据导入器"""
    
    def __init__(self):
        self.data_fetcher = StockDataFetcher()
        self.data_storage = DataStorage()
        logger.info("批量数据导入器初始化完成")
    
    def import_historical_data(self, 
                             start_date: str = None, 
                             end_date: str = None,
                             symbols: List[str] = None,
                             data_types: List[str] = None) -> Dict[str, int]:
        """
        批量导入历史数据
        
        Args:
            start_date: 开始日期 (YYYYMMDD格式)
            end_date: 结束日期 (YYYYMMDD格式)
            symbols: 股票代码列表，None表示所有股票
            data_types: 数据类型列表 ['daily', 'transaction']
        
        Returns:
            导入结果统计
        """
        try:
            if not data_types:
                data_types = ['daily', 'transaction']
            
            if not start_date:
                # 默认导入最近30天的数据
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            logger.info(f"开始批量导入历史数据: {start_date} - {end_date}")
            logger.info(f"数据类型: {data_types}")
            
            # 获取股票列表
            if not symbols:
                logger.info("获取股票列表...")
                stock_list = self.data_fetcher.get_stock_list()
                symbols = stock_list['symbol'].tolist()
                logger.info(f"共 {len(symbols)} 只股票")
            
            results = {
                'total_stocks': len(symbols),
                'daily_data_count': 0,
                'transaction_data_count': 0,
                'failed_stocks': [],
                'success_stocks': []
            }
            
            # 导入日线数据
            if 'daily' in data_types:
                logger.info("开始导入日线数据...")
                daily_results = self._import_daily_data(symbols, start_date, end_date)
                results['daily_data_count'] = daily_results['total_records']
                results['failed_stocks'].extend(daily_results['failed_stocks'])
                results['success_stocks'].extend(daily_results['success_stocks'])
            
            # 导入成交明细数据
            if 'transaction' in data_types:
                logger.info("开始导入成交明细数据...")
                transaction_results = self._import_transaction_data(symbols, start_date, end_date)
                results['transaction_data_count'] = transaction_results['total_records']
                results['failed_stocks'].extend(transaction_results['failed_stocks'])
                results['success_stocks'].extend(transaction_results['success_stocks'])
            
            # 去重失败和成功的股票列表
            results['failed_stocks'] = list(set(results['failed_stocks']))
            results['success_stocks'] = list(set(results['success_stocks']))
            
            logger.info("批量导入完成!")
            logger.info(f"总股票数: {results['total_stocks']}")
            logger.info(f"日线数据: {results['daily_data_count']} 条")
            logger.info(f"成交明细: {results['transaction_data_count']} 条")
            logger.info(f"成功: {len(results['success_stocks'])} 只")
            logger.info(f"失败: {len(results['failed_stocks'])} 只")
            
            return results
            
        except Exception as e:
            logger.error(f"批量导入历史数据失败: {e}")
            raise
    
    def _import_daily_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """导入日线数据"""
        results = {
            'total_records': 0,
            'failed_stocks': [],
            'success_stocks': []
        }
        
        all_daily_data = []
        
        # 使用进度条显示进度
        for symbol in tqdm(symbols, desc="导入日线数据"):
            try:
                daily_data = self.data_fetcher.get_daily_data(symbol, start_date, end_date)
                if not daily_data.empty:
                    all_daily_data.append(daily_data)
                    results['success_stocks'].append(symbol)
                else:
                    results['failed_stocks'].append(symbol)
                
                # 添加延时避免请求过于频繁
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"获取股票 {symbol} 日线数据失败: {e}")
                results['failed_stocks'].append(symbol)
                continue
        
        # 批量保存日线数据
        if all_daily_data:
            try:
                combined_data = pd.concat(all_daily_data, ignore_index=True)
                self.data_storage.save_daily_data(combined_data)
                results['total_records'] = len(combined_data)
                logger.info(f"成功保存日线数据 {len(combined_data)} 条")
            except Exception as e:
                logger.error(f"保存日线数据失败: {e}")
        
        return results
    
    def _import_transaction_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict:
        """导入成交明细数据"""
        results = {
            'total_records': 0,
            'failed_stocks': [],
            'success_stocks': []
        }
        
        # 生成日期范围
        start_dt = datetime.strptime(start_date, '%Y%m%d')
        end_dt = datetime.strptime(end_date, '%Y%m%d')
        date_range = []
        current_dt = start_dt
        while current_dt <= end_dt:
            # 跳过周末
            if current_dt.weekday() < 5:
                date_range.append(current_dt.strftime('%Y%m%d'))
            current_dt += timedelta(days=1)
        
        all_transaction_data = {}
        
        # 使用进度条显示进度
        total_tasks = len(symbols) * len(date_range)
        with tqdm(total=total_tasks, desc="导入成交明细") as pbar:
            for symbol in symbols:
                symbol_success = True
                for trade_date in date_range:
                    try:
                        transaction_data = self.data_fetcher.get_transaction_detail(symbol, trade_date)
                        if not transaction_data.empty:
                            if symbol not in all_transaction_data:
                                all_transaction_data[symbol] = []
                            all_transaction_data[symbol].append(transaction_data)
                        
                        # 添加延时避免请求过于频繁
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"获取股票 {symbol} 在 {trade_date} 的成交明细失败: {e}")
                        symbol_success = False
                    
                    pbar.update(1)
                
                if symbol_success:
                    results['success_stocks'].append(symbol)
                else:
                    results['failed_stocks'].append(symbol)
        
        # 批量保存成交明细数据
        if all_transaction_data:
            try:
                # 合并每个股票的数据
                final_transaction_data = {}
                for symbol, data_list in all_transaction_data.items():
                    if data_list:
                        final_transaction_data[symbol] = pd.concat(data_list, ignore_index=True)
                
                self.data_storage.save_transaction_details(final_transaction_data)
                results['total_records'] = sum(len(df) for df in final_transaction_data.values())
                logger.info(f"成功保存成交明细数据 {results['total_records']} 条")
            except Exception as e:
                logger.error(f"保存成交明细数据失败: {e}")
        
        return results
    
    def import_stock_list(self) -> bool:
        """导入股票列表"""
        try:
            logger.info("开始导入股票列表...")
            stock_list = self.data_fetcher.get_stock_list()
            if not stock_list.empty:
                success = self.data_storage.save_stock_info(stock_list)
                if success:
                    logger.info(f"成功导入股票列表 {len(stock_list)} 只")
                    return True
                else:
                    logger.error("保存股票列表失败")
                    return False
            else:
                logger.error("获取股票列表失败")
                return False
        except Exception as e:
            logger.error(f"导入股票列表失败: {e}")
            return False
    
    def get_import_progress(self) -> Dict:
        """获取导入进度"""
        try:
            stock_count = self.data_storage.get_stock_count()
            daily_count = self.data_storage.get_daily_data_count()
            transaction_count = self.data_storage.get_transaction_detail_count()
            
            return {
                'stock_count': stock_count,
                'daily_data_count': daily_count,
                'transaction_detail_count': transaction_count,
                'latest_trade_date': self.data_storage.get_latest_trade_date()
            }
        except Exception as e:
            logger.error(f"获取导入进度失败: {e}")
            return {}


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量导入历史数据')
    parser.add_argument('--start-date', type=str, help='开始日期 (YYYYMMDD)')
    parser.add_argument('--end-date', type=str, help='结束日期 (YYYYMMDD)')
    parser.add_argument('--symbols', type=str, nargs='+', help='股票代码列表')
    parser.add_argument('--data-types', type=str, nargs='+', 
                       choices=['daily', 'transaction'], 
                       default=['daily', 'transaction'],
                       help='数据类型')
    parser.add_argument('--stock-list', action='store_true', help='只导入股票列表')
    parser.add_argument('--progress', action='store_true', help='显示导入进度')
    
    args = parser.parse_args()
    
    # 设置日志
    from src.config import Config
    Config.setup_logging()
    
    # 验证配置
    try:
        Config.validate_config()
    except Exception as e:
        print(f"配置验证失败: {e}")
        return
    
    # 创建导入器
    importer = BatchImporter()
    
    try:
        if args.progress:
            # 显示进度
            progress = importer.get_import_progress()
            print("\n=== 导入进度 ===")
            print(f"股票数量: {progress.get('stock_count', 0)}")
            print(f"日线数据: {progress.get('daily_data_count', 0)} 条")
            print(f"成交明细: {progress.get('transaction_detail_count', 0)} 条")
            print(f"最新交易日期: {progress.get('latest_trade_date', 'N/A')}")
            
        elif args.stock_list:
            # 只导入股票列表
            success = importer.import_stock_list()
            if success:
                print("股票列表导入成功!")
            else:
                print("股票列表导入失败!")
                
        else:
            # 导入历史数据
            results = importer.import_historical_data(
                start_date=args.start_date,
                end_date=args.end_date,
                symbols=args.symbols,
                data_types=args.data_types
            )
            
            print("\n=== 导入结果 ===")
            print(f"总股票数: {results['total_stocks']}")
            print(f"日线数据: {results['daily_data_count']} 条")
            print(f"成交明细: {results['transaction_data_count']} 条")
            print(f"成功: {len(results['success_stocks'])} 只")
            print(f"失败: {len(results['failed_stocks'])} 只")
            
            if results['failed_stocks']:
                print(f"失败的股票: {', '.join(results['failed_stocks'][:10])}")
                if len(results['failed_stocks']) > 10:
                    print(f"... 还有 {len(results['failed_stocks']) - 10} 只")
    
    except Exception as e:
        print(f"导入失败: {e}")
        logger.error(f"导入失败: {e}")


if __name__ == "__main__":
    main()
