# -*- coding: utf-8 -*-
"""
系统测试脚本
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.data_fetcher import StockDataFetcher
from src.data_storage import DataStorage
from database import db_manager


def test_database_connection():
    """测试数据库连接"""
    print("=== 测试数据库连接 ===")
    try:
        session = db_manager.get_session()
        session.execute("SELECT 1")
        session.close()
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_data_fetcher():
    """测试数据获取"""
    print("\n=== 测试数据获取 ===")
    try:
        fetcher = StockDataFetcher()
        
        # 测试获取股票列表
        print("测试获取股票列表...")
        stock_list = fetcher.get_stock_list()
        if not stock_list.empty:
            print(f"✅ 成功获取股票列表，共 {len(stock_list)} 只股票")
            print(f"示例股票: {stock_list.head(3).to_string()}")
        else:
            print("❌ 获取股票列表失败")
            return False
        
        # 测试获取日线数据
        print("\n测试获取日线数据...")
        test_symbol = stock_list.iloc[0]['symbol']
        daily_data = fetcher.get_daily_data(test_symbol)
        if not daily_data.empty:
            print(f"✅ 成功获取股票 {test_symbol} 日线数据 {len(daily_data)} 条")
        else:
            print(f"❌ 获取股票 {test_symbol} 日线数据失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据获取测试失败: {e}")
        return False


def test_data_storage():
    """测试数据存储"""
    print("\n=== 测试数据存储 ===")
    try:
        storage = DataStorage()
        
        # 测试获取股票数量
        stock_count = storage.get_stock_count()
        print(f"当前股票数量: {stock_count}")
        
        # 测试获取日线数据数量
        daily_count = storage.get_daily_data_count()
        print(f"当前日线数据数量: {daily_count}")
        
        # 测试获取成交明细数量
        transaction_count = storage.get_transaction_detail_count()
        print(f"当前成交明细数量: {transaction_count}")
        
        print("✅ 数据存储测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据存储测试失败: {e}")
        return False


def test_system_integration():
    """测试系统集成"""
    print("\n=== 测试系统集成 ===")
    try:
        # 测试完整的数据采集流程
        fetcher = StockDataFetcher()
        storage = DataStorage()
        
        # 获取少量股票进行测试
        stock_list = fetcher.get_stock_list()
        test_symbols = stock_list['symbol'].head(5).tolist()
        
        print(f"测试股票: {test_symbols}")
        
        # 获取日线数据
        daily_data = fetcher.get_today_daily_data(test_symbols)
        if not daily_data.empty:
            print(f"✅ 获取日线数据成功: {len(daily_data)} 条")
            # 保存数据
            if storage.save_daily_data(daily_data):
                print("✅ 保存日线数据成功")
            else:
                print("❌ 保存日线数据失败")
        else:
            print("⚠️  今日没有日线数据（可能是非交易日）")
        
        return True
        
    except Exception as e:
        print(f"❌ 系统集成测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("量化金融系统测试")
    print("=" * 50)
    
    # 设置日志
    Config.setup_logging()
    
    # 验证配置
    try:
        Config.validate_config()
        print("✅ 配置验证通过")
    except Exception as e:
        print(f"❌ 配置验证失败: {e}")
        return
    
    # 执行测试
    tests = [
        test_database_connection,
        test_data_fetcher,
        test_data_storage,
        test_system_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统运行正常")
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接")
    
    # 关闭数据库连接
    db_manager.close()


if __name__ == "__main__":
    main()
