# -*- coding: utf-8 -*-
"""
配置管理模块
"""
import os
from dotenv import load_dotenv
from loguru import logger
import sys

# 加载环境变量
load_dotenv()

class Config:
    """配置类"""
    
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'quantitative_finance')
    
    # Tushare配置
    TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/quantitative_finance.log')
    
    # 数据源配置
    DATA_SOURCE = os.getenv('DATA_SOURCE', 'akshare')
    
    # 任务调度配置
    DAILY_TASK_TIME = os.getenv('DAILY_TASK_TIME', '15:30')
    TRANSACTION_TASK_INTERVAL = int(os.getenv('TRANSACTION_TASK_INTERVAL', '30'))
    
    # 数据获取配置
    MAX_RETRY_COUNT = int(os.getenv('MAX_RETRY_COUNT', '3'))
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.0'))
    
    @classmethod
    def setup_logging(cls):
        """设置日志配置"""
        try:
            # 移除默认的日志处理器
            logger.remove()
            
            # 添加控制台输出
            logger.add(
                sys.stdout,
                level=cls.LOG_LEVEL,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                colorize=True
            )
            
            # 添加文件输出
            log_dir = os.path.dirname(cls.LOG_FILE)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            logger.add(
                cls.LOG_FILE,
                level=cls.LOG_LEVEL,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                rotation="1 day",
                retention="30 days",
                compression="zip"
            )
            
            logger.info("日志配置完成")
            
        except Exception as e:
            print(f"日志配置失败: {e}")
    
    @classmethod
    def validate_config(cls):
        """验证配置"""
        errors = []
        
        # 检查数据库配置
        if not cls.DB_HOST:
            errors.append("DB_HOST 未配置")
        if not cls.DB_USER:
            errors.append("DB_USER 未配置")
        if not cls.DB_NAME:
            errors.append("DB_NAME 未配置")
        
        # 检查日志配置
        if not cls.LOG_LEVEL:
            errors.append("LOG_LEVEL 未配置")
        
        # 检查数据源配置
        if cls.DATA_SOURCE not in ['akshare', 'tushare']:
            errors.append(f"不支持的数据源: {cls.DATA_SOURCE}")
        
        if errors:
            raise ValueError(f"配置验证失败: {', '.join(errors)}")
        
        logger.info("配置验证通过")
    
    @classmethod
    def print_config(cls):
        """打印配置信息"""
        logger.info("当前配置:")
        logger.info(f"  数据库: {cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        logger.info(f"  数据源: {cls.DATA_SOURCE}")
        logger.info(f"  日志级别: {cls.LOG_LEVEL}")
        logger.info(f"  日志文件: {cls.LOG_FILE}")
        logger.info(f"  每日任务时间: {cls.DAILY_TASK_TIME}")
        logger.info(f"  成交明细采集间隔: {cls.TRANSACTION_TASK_INTERVAL} 分钟")
