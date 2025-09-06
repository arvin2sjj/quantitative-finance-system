# -*- coding: utf-8 -*-
"""
股票数据获取模块
"""
import akshare as ak
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from loguru import logger
import time
import os


class StockDataFetcher:
    """股票数据获取器"""
    
    def __init__(self):
        self.data_source = os.getenv('DATA_SOURCE', 'akshare')
        logger.info(f"初始化数据获取器，数据源: {self.data_source}")
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            logger.info("开始获取股票列表...")
            
            if self.data_source == 'akshare':
                # 获取沪深A股列表
                stock_list = ak.stock_info_a_code_name()
                stock_list.columns = ['symbol', 'name']
                
                # 添加市场信息
                stock_list['market'] = stock_list['symbol'].apply(
                    lambda x: 'SH' if x.startswith(('60', '68', '90')) else 'SZ'
                )
                
                logger.info(f"成功获取股票列表，共 {len(stock_list)} 只股票")
                return stock_list
            else:
                raise ValueError(f"不支持的数据源: {self.data_source}")
                
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_daily_data(self, symbol: str, start_date: str = None, end_date: str = None, max_retries: int = 3) -> pd.DataFrame:
        """获取股票日线数据"""
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')
            
            logger.info(f"获取股票 {symbol} 日线数据: {start_date} - {end_date}")
            
            if self.data_source == 'akshare':
                # 重试机制
                for attempt in range(max_retries):
                    try:
                        # 获取日线数据
                        daily_data = ak.stock_zh_a_hist(
                            symbol=symbol,
                            period="daily",
                            start_date=start_date,
                            end_date=end_date,
                            adjust="qfq"  # 前复权
                        )
                        break  # 成功则跳出重试循环
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logger.warning(f"获取股票 {symbol} 日线数据失败，第 {attempt + 1} 次重试: {e}")
                            time.sleep(2 ** attempt)  # 指数退避
                            continue
                        else:
                            raise e
                
                if daily_data.empty:
                    logger.warning(f"股票 {symbol} 没有数据")
                    return pd.DataFrame()
                
                # 检查并重命名列
                expected_columns = [
                    'trade_date', 'open_price', 'close_price', 'high_price', 
                    'low_price', 'volume', 'amount', 'amplitude', 'pct_change', 
                    'change_amount', 'turnover'
                ]
                
                # 如果列数不匹配，使用原始列名
                if len(daily_data.columns) == len(expected_columns):
                    daily_data.columns = expected_columns
                else:
                    logger.warning(f"股票 {symbol} 数据列数不匹配，使用原始列名")
                    # 尝试映射常见的列名
                    column_mapping = {
                        '日期': 'trade_date',
                        '开盘': 'open_price',
                        '收盘': 'close_price',
                        '最高': 'high_price',
                        '最低': 'low_price',
                        '成交量': 'volume',
                        '成交额': 'amount',
                        '涨跌幅': 'pct_change',
                        '涨跌额': 'change_amount',
                        '振幅': 'amplitude',
                        '换手率': 'turnover'
                    }
                    
                    # 重命名匹配的列
                    for old_name, new_name in column_mapping.items():
                        if old_name in daily_data.columns:
                            daily_data = daily_data.rename(columns={old_name: new_name})
                
                # 转换日期格式
                daily_data['trade_date'] = pd.to_datetime(daily_data['trade_date']).dt.date
                daily_data['symbol'] = symbol
                
                # 选择需要的列
                columns = ['symbol', 'trade_date', 'open_price', 'high_price', 
                          'low_price', 'close_price', 'volume', 'amount', 'pct_change']
                daily_data = daily_data[columns]
                
                logger.info(f"成功获取股票 {symbol} 日线数据 {len(daily_data)} 条")
                return daily_data
                
            else:
                raise ValueError(f"不支持的数据源: {self.data_source}")
                
        except Exception as e:
            logger.error(f"获取股票 {symbol} 日线数据失败: {e}")
            return pd.DataFrame()
    
    def get_transaction_detail(self, symbol: str, trade_date: str = None) -> pd.DataFrame:
        """获取股票成交明细"""
        try:
            if not trade_date:
                trade_date = datetime.now().strftime('%Y%m%d')
            
            logger.info(f"获取股票 {symbol} 成交明细: {trade_date}")
            
            if self.data_source == 'akshare':
                # 获取成交明细
                detail_data = ak.stock_zh_a_tick_tx(
                    symbol=symbol,
                    trade_date=trade_date
                )
                
                if detail_data.empty:
                    logger.warning(f"股票 {symbol} 在 {trade_date} 没有成交明细数据")
                    return pd.DataFrame()
                
                # 重命名列
                detail_data.columns = [
                    'trade_time', 'price', 'volume', 'amount', 'direction'
                ]
                
                # 转换时间格式
                detail_data['trade_time'] = pd.to_datetime(
                    f"{trade_date} " + detail_data['trade_time']
                )
                detail_data['trade_date'] = pd.to_datetime(trade_date).date()
                detail_data['symbol'] = symbol
                
                # 选择需要的列
                columns = ['symbol', 'trade_date', 'trade_time', 'price', 
                          'volume', 'amount', 'direction']
                detail_data = detail_data[columns]
                
                logger.info(f"成功获取股票 {symbol} 成交明细 {len(detail_data)} 条")
                return detail_data
                
            else:
                raise ValueError(f"不支持的数据源: {self.data_source}")
                
        except Exception as e:
            logger.error(f"获取股票 {symbol} 成交明细失败: {e}")
            return pd.DataFrame()
    
    def get_today_transaction_details(self, symbols: List[str] = None) -> Dict[str, pd.DataFrame]:
        """获取今日所有股票的成交明细"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            logger.info(f"开始获取今日 {today} 成交明细数据")
            
            if not symbols:
                # 获取股票列表
                stock_list = self.get_stock_list()
                symbols = stock_list['symbol'].tolist()
            
            all_details = {}
            success_count = 0
            failed_count = 0
            
            for i, symbol in enumerate(symbols):
                try:
                    detail_data = self.get_transaction_detail(symbol, today)
                    if not detail_data.empty:
                        all_details[symbol] = detail_data
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    # 添加延时避免请求过于频繁
                    if i % 10 == 0:
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"获取股票 {symbol} 成交明细失败: {e}")
                    failed_count += 1
                    continue
            
            logger.info(f"成交明细获取完成: 成功 {success_count} 只，失败 {failed_count} 只")
            return all_details
            
        except Exception as e:
            logger.error(f"获取今日成交明细失败: {e}")
            raise
    
    def get_today_daily_data(self, symbols: List[str] = None) -> pd.DataFrame:
        """获取今日所有股票的日线数据"""
        try:
            today = datetime.now().strftime('%Y%m%d')
            logger.info(f"开始获取今日 {today} 日线数据")
            
            if not symbols:
                # 获取股票列表
                stock_list = self.get_stock_list()
                symbols = stock_list['symbol'].tolist()
            
            all_daily_data = []
            success_count = 0
            failed_count = 0
            
            for i, symbol in enumerate(symbols):
                try:
                    daily_data = self.get_daily_data(symbol, today, today)
                    if not daily_data.empty:
                        all_daily_data.append(daily_data)
                        success_count += 1
                    else:
                        failed_count += 1
                    
                    # 添加延时避免请求过于频繁
                    if i % 10 == 0:
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"获取股票 {symbol} 日线数据失败: {e}")
                    failed_count += 1
                    continue
            
            if all_daily_data:
                result = pd.concat(all_daily_data, ignore_index=True)
                logger.info(f"日线数据获取完成: 成功 {success_count} 只，失败 {failed_count} 只")
                return result
            else:
                logger.warning("没有获取到任何日线数据")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取今日日线数据失败: {e}")
            raise
