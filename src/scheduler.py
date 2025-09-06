# -*- coding: utf-8 -*-
"""
定时任务调度模块
"""
import schedule
import time
from datetime import datetime, date, timedelta
from loguru import logger
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import StockDataFetcher
from src.data_storage import DataStorage


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.data_fetcher = StockDataFetcher()
        self.data_storage = DataStorage()
        logger.info("任务调度器初始化完成")
    
    def daily_data_collection_task(self):
        """每日数据采集任务"""
        try:
            logger.info("开始执行每日数据采集任务")
            
            # 检查是否是交易日
            if not self._is_trading_day():
                logger.info("今日非交易日，跳过数据采集")
                return
            
            # 获取股票列表
            logger.info("获取股票列表...")
            stock_list = self.data_fetcher.get_stock_list()
            if stock_list.empty:
                logger.error("获取股票列表失败")
                return
            
            # 保存股票基本信息（每日更新）
            logger.info("保存股票基本信息...")
            self.data_storage.save_stock_info(stock_list)
            
            # 获取今日日线数据
            logger.info("获取今日日线数据...")
            daily_data = self.data_fetcher.get_today_daily_data()
            if not daily_data.empty:
                self.data_storage.save_daily_data(daily_data)
                logger.info(f"成功保存日线数据 {len(daily_data)} 条")
            else:
                logger.warning("今日没有日线数据")
            
            # 获取今日成交明细
            logger.info("获取今日成交明细...")
            transaction_details = self.data_fetcher.get_today_transaction_details()
            if transaction_details:
                self.data_storage.save_transaction_details(transaction_details)
                total_records = sum(len(df) for df in transaction_details.values())
                logger.info(f"成功保存成交明细数据 {total_records} 条")
            else:
                logger.warning("今日没有成交明细数据")
            
            logger.info("每日数据采集任务完成")
            
        except Exception as e:
            logger.error(f"每日数据采集任务失败: {e}")
            self.data_storage.save_system_log("ERROR", f"每日数据采集任务失败: {e}", "scheduler", "daily_data_collection_task")
    
    def transaction_detail_collection_task(self):
        """成交明细采集任务（盘中执行）"""
        try:
            logger.info("开始执行成交明细采集任务")
            
            # 检查是否是交易日和交易时间
            if not self._is_trading_time():
                logger.info("当前非交易时间，跳过成交明细采集")
                return
            
            # 获取股票列表
            stock_list = self.data_fetcher.get_stock_list()
            if stock_list.empty:
                logger.error("获取股票列表失败")
                return
            
            # 获取成交明细（只获取部分活跃股票）
            symbols = stock_list['symbol'].head(100).tolist()  # 限制数量避免请求过多
            transaction_details = self.data_fetcher.get_today_transaction_details(symbols)
            
            if transaction_details:
                self.data_storage.save_transaction_details(transaction_details)
                total_records = sum(len(df) for df in transaction_details.values())
                logger.info(f"成功保存成交明细数据 {total_records} 条")
            else:
                logger.warning("没有成交明细数据")
            
            logger.info("成交明细采集任务完成")
            
        except Exception as e:
            logger.error(f"成交明细采集任务失败: {e}")
            self.data_storage.save_system_log("ERROR", f"成交明细采集任务失败: {e}", "scheduler", "transaction_detail_collection_task")
    
    def _is_trading_day(self) -> bool:
        """检查是否是交易日"""
        today = date.today()
        weekday = today.weekday()
        
        # 周末不是交易日
        if weekday >= 5:  # 5=Saturday, 6=Sunday
            return False
        
        # 这里可以添加节假日判断逻辑
        # 暂时简单处理，实际应用中需要维护节假日列表
        
        return True
    
    def _is_trading_time(self) -> bool:
        """检查是否是交易时间"""
        now = datetime.now()
        weekday = now.weekday()
        
        # 周末不是交易日
        if weekday >= 5:
            return False
        
        # 交易时间：9:30-11:30, 13:00-15:00
        current_time = now.time()
        morning_start = datetime.strptime("09:30", "%H:%M").time()
        morning_end = datetime.strptime("11:30", "%H:%M").time()
        afternoon_start = datetime.strptime("13:00", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()
        
        return (morning_start <= current_time <= morning_end) or \
               (afternoon_start <= current_time <= afternoon_end)
    
    def setup_schedule(self):
        """设置定时任务"""
        try:
            # 每日收盘后执行数据采集（15:30）
            schedule.every().day.at("15:30").do(self.daily_data_collection_task)
            
            # 交易时间内每30分钟执行一次成交明细采集
            schedule.every(30).minutes.do(self.transaction_detail_collection_task)
            
            # 每日开盘前更新股票列表（9:00）
            schedule.every().day.at("09:00").do(self._update_stock_list)
            
            logger.info("定时任务设置完成")
            logger.info("- 每日15:30执行数据采集")
            logger.info("- 交易时间每30分钟执行成交明细采集")
            logger.info("- 每日09:00更新股票列表")
            
        except Exception as e:
            logger.error(f"设置定时任务失败: {e}")
    
    def _update_stock_list(self):
        """更新股票列表"""
        try:
            logger.info("开始更新股票列表")
            stock_list = self.data_fetcher.get_stock_list()
            if not stock_list.empty:
                self.data_storage.save_stock_info(stock_list)
                logger.info("股票列表更新完成")
            else:
                logger.error("获取股票列表失败")
        except Exception as e:
            logger.error(f"更新股票列表失败: {e}")
    
    def run_scheduler(self):
        """运行调度器"""
        try:
            logger.info("启动定时任务调度器")
            self.setup_schedule()
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止调度器")
        except Exception as e:
            logger.error(f"调度器运行失败: {e}")
    
    def run_once(self):
        """执行一次数据采集（用于测试）"""
        try:
            logger.info("执行一次性数据采集")
            self.daily_data_collection_task()
        except Exception as e:
            logger.error(f"一次性数据采集失败: {e}")


if __name__ == "__main__":
    scheduler = TaskScheduler()
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 执行一次数据采集
        scheduler.run_once()
    else:
        # 运行定时调度器
        scheduler.run_scheduler()
