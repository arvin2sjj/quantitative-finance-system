# 量化金融系统

一个基于Python的量化金融数据采集系统，用于每日定时获取沪深股票成交明细并存储到MySQL数据库。

## 功能特性

- 🚀 **自动数据采集**: 每日定时获取沪深股票成交明细和日线数据
- 📊 **多数据源支持**: 支持AKShare和Tushare数据源
- 🗄️ **MySQL存储**: 结构化存储股票数据，支持高效查询
- ⏰ **智能调度**: 基于交易时间的智能任务调度
- 📝 **完整日志**: 详细的系统日志和错误处理
- 🔧 **灵活配置**: 支持环境变量配置
- 📈 **批量导入**: 支持一次性批量导入历史数据
- 🎯 **进度监控**: 实时显示导入进度和统计信息

## 系统架构

```
quantitative_finance_system/
├── src/                    # 核心模块
│   ├── data_fetcher.py    # 数据获取模块
│   ├── data_storage.py    # 数据存储模块
│   ├── scheduler.py       # 任务调度模块
│   ├── batch_importer.py  # 批量导入模块
│   └── config.py          # 配置管理模块
├── database/              # 数据库模块
│   ├── models.py          # 数据模型
│   ├── connection.py      # 数据库连接
│   └── init_db.py         # 数据库初始化
├── logs/                  # 日志目录
├── main.py               # 主程序入口
├── batch_import.py       # 批量导入工具
├── requirements.txt      # 依赖包
├── config.env.example    # 配置文件示例
└── BATCH_IMPORT_GUIDE.md # 批量导入使用指南
```

## 数据库表结构

### 1. stock_info - 股票基本信息表
- `symbol`: 股票代码
- `name`: 股票名称
- `market`: 市场类型(SH/SZ)
- `industry`: 所属行业
- `list_date`: 上市日期

### 2. stock_daily_data - 股票日线数据表
- `symbol`: 股票代码
- `trade_date`: 交易日期
- `open_price`: 开盘价
- `high_price`: 最高价
- `low_price`: 最低价
- `close_price`: 收盘价
- `volume`: 成交量
- `amount`: 成交额
- `pct_change`: 涨跌幅

### 3. stock_transaction_detail - 股票成交明细表
- `symbol`: 股票代码
- `trade_date`: 交易日期
- `trade_time`: 成交时间
- `price`: 成交价格
- `volume`: 成交数量
- `amount`: 成交金额
- `direction`: 买卖方向(B/S)

### 4. system_log - 系统日志表
- `level`: 日志级别
- `message`: 日志消息
- `module`: 模块名称
- `function`: 函数名称
- `created_at`: 创建时间

## 安装和配置

### 1. 环境要求
- Python 3.8+
- MySQL 5.7+

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置数据库
复制配置文件并修改：
```bash
cp config.env.example .env
```

编辑 `.env` 文件：
```env
# MySQL数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=quantitative_finance

# 数据源配置
DATA_SOURCE=akshare

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/quantitative_finance.log
```

### 4. 创建数据库
在MySQL中创建数据库：
```sql
CREATE DATABASE quantitative_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 初始化数据库表
```bash
python main.py --init
```

## 使用方法

### 1. 运行定时调度器
```bash
python main.py --scheduler
```

### 2. 执行一次数据采集
```bash
python main.py --once
```

### 3. 查看系统状态
```bash
python main.py --status
```

### 4. 批量导入历史数据
```bash
# 导入股票列表
python batch_import.py --stock-list

# 导入指定股票的历史数据
python batch_import.py --symbols 000001 000002 --start-date 20240901 --end-date 20240906

# 导入所有股票的日线数据（最近30天）
python batch_import.py --data-types daily

# 查看导入进度
python batch_import.py --progress
```

### 5. 数据库管理
```bash
# 创建表
python database/init_db.py --create

# 删除表
python database/init_db.py --drop
```

## 任务调度

系统会自动执行以下任务：

1. **每日15:30**: 执行完整数据采集
   - 更新股票列表
   - 获取当日日线数据
   - 获取当日成交明细

2. **交易时间每30分钟**: 执行成交明细采集
   - 获取活跃股票的成交明细

3. **每日09:00**: 更新股票列表
   - 获取最新的股票基本信息

## 数据源说明

### AKShare
- 免费开源
- 数据更新及时
- 支持沪深股票数据
- 无需注册

### Tushare (可选)
- 需要注册获取Token
- 数据质量较高
- 支持更多数据接口

## 注意事项

1. **请求频率**: 系统已内置请求延时，避免过于频繁的API调用
2. **交易时间**: 系统会自动判断交易日和交易时间
3. **错误处理**: 完善的错误处理和日志记录
4. **数据完整性**: 支持数据去重和增量更新

## 监控和维护

### 日志文件
- 系统日志: `logs/quantitative_finance.log`
- 自动轮转: 每日一个文件
- 保留期限: 30天

### 数据库监控
```sql
-- 查看数据统计
SELECT 
    COUNT(*) as stock_count 
FROM stock_info;

SELECT 
    trade_date, 
    COUNT(*) as daily_count 
FROM stock_daily_data 
GROUP BY trade_date 
ORDER BY trade_date DESC 
LIMIT 10;

SELECT 
    trade_date, 
    COUNT(*) as transaction_count 
FROM stock_transaction_detail 
GROUP BY trade_date 
ORDER BY trade_date DESC 
LIMIT 10;
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库配置
   - 确认MySQL服务运行状态
   - 验证用户权限

2. **数据获取失败**
   - 检查网络连接
   - 验证数据源配置
   - 查看错误日志

3. **任务调度异常**
   - 检查系统时间
   - 查看调度器日志
   - 验证任务配置

## 扩展功能

系统支持以下扩展：

1. **新增数据源**: 在 `data_fetcher.py` 中添加新的数据源
2. **自定义指标**: 在 `models.py` 中添加新的数据表
3. **告警机制**: 集成邮件或短信告警
4. **数据可视化**: 集成图表展示功能
5. **API接口**: 提供RESTful API接口

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。
