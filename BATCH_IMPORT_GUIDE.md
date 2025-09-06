# 批量导入历史数据使用指南

## 概述

本系统提供了强大的批量导入功能，可以一次性将沪深股票的历史成交数据写入MySQL数据库。

## 功能特性

- ✅ 支持批量导入股票基本信息
- ✅ 支持批量导入日线数据
- ✅ 支持批量导入成交明细数据
- ✅ 智能进度显示
- ✅ 错误处理和重试机制
- ✅ 灵活的数据范围选择
- ✅ 支持指定股票代码

## 使用方法

### 1. 环境准备

确保MySQL服务已启动并配置正确：

```bash
# 启动MySQL服务（如果使用我们配置的MySQL）
mysqld --datadir=/Users/vicky/mysql_data --socket=/Users/vicky/mysql_data/mysql.sock --port=3306 &

# 激活虚拟环境
source venv/bin/activate
```

### 2. 初始化数据库

```bash
python main.py --init
```

### 3. 导入股票列表

```bash
python batch_import.py --stock-list
```

### 4. 批量导入历史数据

#### 导入所有股票的日线数据（最近30天）

```bash
python batch_import.py
```

#### 导入指定日期范围的日线数据

```bash
python batch_import.py --start-date 20240901 --end-date 20240906
```

#### 导入指定股票的数据

```bash
python batch_import.py --symbols 000001 000002 600000 --start-date 20240901 --end-date 20240906
```

#### 只导入日线数据（不导入成交明细）

```bash
python batch_import.py --data-types daily
```

#### 只导入成交明细数据

```bash
python batch_import.py --data-types transaction
```

### 5. 查看导入进度

```bash
python batch_import.py --progress
```

## 命令行参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--start-date` | 开始日期 (YYYYMMDD格式) | `--start-date 20240901` |
| `--end-date` | 结束日期 (YYYYMMDD格式) | `--end-date 20240906` |
| `--symbols` | 股票代码列表 | `--symbols 000001 000002` |
| `--data-types` | 数据类型 | `--data-types daily transaction` |
| `--stock-list` | 只导入股票列表 | `--stock-list` |
| `--progress` | 显示导入进度 | `--progress` |

## 数据说明

### 股票基本信息表 (stock_info)
- `symbol`: 股票代码
- `name`: 股票名称
- `market`: 市场类型 (SH/SZ)
- `industry`: 所属行业
- `list_date`: 上市日期

### 日线数据表 (stock_daily_data)
- `symbol`: 股票代码
- `trade_date`: 交易日期
- `open_price`: 开盘价
- `high_price`: 最高价
- `low_price`: 最低价
- `close_price`: 收盘价
- `volume`: 成交量
- `amount`: 成交额
- `pct_change`: 涨跌幅

### 成交明细表 (stock_transaction_detail)
- `symbol`: 股票代码
- `trade_date`: 交易日期
- `trade_time`: 成交时间
- `price`: 成交价格
- `volume`: 成交数量
- `amount`: 成交金额
- `direction`: 买卖方向 (B/S)

## 性能优化建议

1. **分批导入**: 对于大量数据，建议分批导入，避免内存溢出
2. **网络延时**: 系统已内置请求延时，避免API限制
3. **错误处理**: 失败的股票会自动记录，可以单独重试
4. **进度监控**: 使用 `--progress` 参数监控导入进度

## 示例场景

### 场景1: 导入所有股票最近一周的日线数据

```bash
python batch_import.py --start-date 20240901 --end-date 20240906 --data-types daily
```

### 场景2: 导入指定股票的完整历史数据

```bash
python batch_import.py --symbols 000001 600000 --start-date 20240101 --end-date 20240906
```

### 场景3: 只导入成交明细数据

```bash
python batch_import.py --data-types transaction --start-date 20240906 --end-date 20240906
```

## 故障排除

### 1. MySQL连接失败
- 检查MySQL服务是否启动
- 检查配置文件中的数据库连接信息
- 确保数据库用户权限正确

### 2. 数据获取失败
- 检查网络连接
- 确认数据源API可用性
- 查看日志文件了解详细错误信息

### 3. 内存不足
- 减少单次导入的股票数量
- 分批导入数据
- 增加系统内存

## 日志文件

系统日志保存在 `logs/quantitative_finance.log`，包含详细的执行信息和错误信息。

## 注意事项

1. 首次导入建议先导入少量数据测试
2. 大量数据导入可能需要较长时间，请耐心等待
3. 建议在非交易时间进行批量导入，避免影响实时数据获取
4. 定期备份数据库，防止数据丢失
