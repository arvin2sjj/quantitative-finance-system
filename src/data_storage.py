# -*- coding: utf-8 -*-
"""
数据存储模块
"""
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from loguru import logger
from database import db_manager, StockInfo, StockDailyData, StockTransactionDetail, SystemLog


class DataStorage:
    """数据存储器"""
    
    def __init__(self):
        self.db_manager = db_manager
        logger.info("数据存储器初始化完成")
    
    def save_stock_info(self, stock_data: pd.DataFrame) -> bool:
        """保存股票基本信息"""
        try:
            session = self.db_manager.get_session()
            
            # 清空现有数据
            session.query(StockInfo).delete()
            
            # 批量插入新数据
            stock_records = []
            for _, row in stock_data.iterrows():
                stock_record = StockInfo(
                    symbol=row['symbol'],
                    name=row['name'],
                    market=row['market']
                )
                stock_records.append(stock_record)
            
            session.bulk_save_objects(stock_records)
            session.commit()
            
            logger.info(f"成功保存股票基本信息 {len(stock_records)} 条")
            return True
            
        except Exception as e:
            logger.error(f"保存股票基本信息失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_daily_data(self, daily_data: pd.DataFrame) -> bool:
        """保存日线数据"""
        try:
            if daily_data.empty:
                logger.warning("日线数据为空，跳过保存")
                return True
            
            session = self.db_manager.get_session()
            
            # 批量插入数据
            daily_records = []
            for _, row in daily_data.iterrows():
                daily_record = StockDailyData(
                    symbol=row['symbol'],
                    trade_date=row['trade_date'],
                    open_price=row['open_price'],
                    high_price=row['high_price'],
                    low_price=row['low_price'],
                    close_price=row['close_price'],
                    volume=row['volume'],
                    amount=row['amount'],
                    pct_change=row['pct_change']
                )
                daily_records.append(daily_record)
            
            session.bulk_save_objects(daily_records)
            session.commit()
            
            logger.info(f"成功保存日线数据 {len(daily_records)} 条")
            return True
            
        except Exception as e:
            logger.error(f"保存日线数据失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def save_transaction_details(self, transaction_data: Dict[str, pd.DataFrame]) -> bool:
        """保存成交明细数据"""
        try:
            if not transaction_data:
                logger.warning("成交明细数据为空，跳过保存")
                return True
            
            session = self.db_manager.get_session()
            
            total_records = 0
            for symbol, data in transaction_data.items():
                if data.empty:
                    continue
                
                # 批量插入数据
                detail_records = []
                for _, row in data.iterrows():
                    detail_record = StockTransactionDetail(
                        symbol=row['symbol'],
                        trade_date=row['trade_date'],
                        trade_time=row['trade_time'],
                        price=row['price'],
                        volume=row['volume'],
                        amount=row['amount'],
                        direction=row['direction']
                    )
                    detail_records.append(detail_record)
                
                session.bulk_save_objects(detail_records)
                total_records += len(detail_records)
            
            session.commit()
            logger.info(f"成功保存成交明细数据 {total_records} 条")
            return True
            
        except Exception as e:
            logger.error(f"保存成交明细数据失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_latest_trade_date(self) -> Optional[date]:
        """获取最新的交易日期"""
        try:
            session = self.db_manager.get_session()
            
            latest_record = session.query(StockDailyData.trade_date)\
                .order_by(StockDailyData.trade_date.desc())\
                .first()
            
            if latest_record:
                return latest_record[0]
            return None
            
        except Exception as e:
            logger.error(f"获取最新交易日期失败: {e}")
            return None
        finally:
            session.close()
    
    def check_data_exists(self, table_class, **filters) -> bool:
        """检查数据是否已存在"""
        try:
            session = self.db_manager.get_session()
            
            query = session.query(table_class)
            for key, value in filters.items():
                query = query.filter(getattr(table_class, key) == value)
            
            exists = query.first() is not None
            return exists
            
        except Exception as e:
            logger.error(f"检查数据是否存在失败: {e}")
            return False
        finally:
            session.close()
    
    def save_system_log(self, level: str, message: str, module: str = None, function: str = None):
        """保存系统日志到数据库"""
        try:
            session = self.db_manager.get_session()
            
            log_record = SystemLog(
                level=level,
                message=message,
                module=module,
                function=function
            )
            
            session.add(log_record)
            session.commit()
            
        except Exception as e:
            logger.error(f"保存系统日志失败: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_stock_count(self) -> int:
        """获取股票数量"""
        try:
            session = self.db_manager.get_session()
            count = session.query(StockInfo).count()
            return count
        except Exception as e:
            logger.error(f"获取股票数量失败: {e}")
            return 0
        finally:
            session.close()
    
    def get_daily_data_count(self, trade_date: date = None) -> int:
        """获取日线数据数量"""
        try:
            session = self.db_manager.get_session()
            query = session.query(StockDailyData)
            
            if trade_date:
                query = query.filter(StockDailyData.trade_date == trade_date)
            
            count = query.count()
            return count
        except Exception as e:
            logger.error(f"获取日线数据数量失败: {e}")
            return 0
        finally:
            session.close()
    
    def get_transaction_detail_count(self, trade_date: date = None) -> int:
        """获取成交明细数据数量"""
        try:
            session = self.db_manager.get_session()
            query = session.query(StockTransactionDetail)
            
            if trade_date:
                query = query.filter(StockTransactionDetail.trade_date == trade_date)
            
            count = query.count()
            return count
        except Exception as e:
            logger.error(f"获取成交明细数据数量失败: {e}")
            return 0
        finally:
            session.close()
