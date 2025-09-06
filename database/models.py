# -*- coding: utf-8 -*-
"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class StockInfo(Base):
    """股票基本信息表"""
    __tablename__ = 'stock_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, comment='股票代码')
    name = Column(String(50), nullable=False, comment='股票名称')
    market = Column(String(10), nullable=False, comment='市场类型(SH/SZ)')
    industry = Column(String(50), comment='所属行业')
    list_date = Column(Date, comment='上市日期')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    __table_args__ = (
        Index('idx_symbol', 'symbol'),
        Index('idx_market', 'market'),
    )


class StockDailyData(Base):
    """股票日线数据表"""
    __tablename__ = 'stock_daily_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, comment='股票代码')
    trade_date = Column(Date, nullable=False, comment='交易日期')
    open_price = Column(Float, comment='开盘价')
    high_price = Column(Float, comment='最高价')
    low_price = Column(Float, comment='最低价')
    close_price = Column(Float, comment='收盘价')
    volume = Column(Integer, comment='成交量')
    amount = Column(Float, comment='成交额')
    pct_change = Column(Float, comment='涨跌幅')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    
    __table_args__ = (
        Index('idx_symbol_date', 'symbol', 'trade_date'),
        Index('idx_trade_date', 'trade_date'),
    )


class StockTransactionDetail(Base):
    """股票成交明细表"""
    __tablename__ = 'stock_transaction_detail'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False, comment='股票代码')
    trade_date = Column(Date, nullable=False, comment='交易日期')
    trade_time = Column(DateTime, nullable=False, comment='成交时间')
    price = Column(Float, nullable=False, comment='成交价格')
    volume = Column(Integer, nullable=False, comment='成交数量')
    amount = Column(Float, nullable=False, comment='成交金额')
    direction = Column(String(2), comment='买卖方向(B/S)')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    
    __table_args__ = (
        Index('idx_symbol_date_time', 'symbol', 'trade_date', 'trade_time'),
        Index('idx_trade_date', 'trade_date'),
    )


class SystemLog(Base):
    """系统日志表"""
    __tablename__ = 'system_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(10), nullable=False, comment='日志级别')
    message = Column(Text, nullable=False, comment='日志消息')
    module = Column(String(50), comment='模块名称')
    function = Column(String(50), comment='函数名称')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    
    __table_args__ = (
        Index('idx_level', 'level'),
        Index('idx_created_at', 'created_at'),
    )
