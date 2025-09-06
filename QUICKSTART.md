# 快速开始指南

## 1. 环境准备

### 安装Python依赖
```bash
pip install -r requirements.txt
```

### 配置MySQL数据库
1. 安装MySQL 5.7+
2. 创建数据库：
```sql
CREATE DATABASE quantitative_finance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. 配置系统

### 复制配置文件
```bash
cp config.env.example .env
```

### 编辑配置文件
```bash
nano .env
```

修改以下配置：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=quantitative_finance
```

## 3. 初始化系统

### 初始化数据库表
```bash
python main.py --init
```

### 测试系统
```bash
python test_system.py
```

## 4. 运行系统

### 方式一：使用启动脚本
```bash
./start.sh
```

### 方式二：手动启动
```bash
# 运行定时调度器
python main.py --scheduler

# 或者执行一次数据采集
python main.py --once
```

## 5. 监控系统

### 查看系统状态
```bash
python main.py --status
```

### 查看日志
```bash
tail -f logs/quantitative_finance.log
```

## 6. 常见问题

### 数据库连接失败
- 检查MySQL服务是否运行
- 验证数据库配置信息
- 确认用户权限

### 数据获取失败
- 检查网络连接
- 验证数据源配置
- 查看错误日志

### 任务调度异常
- 检查系统时间
- 查看调度器日志
- 验证任务配置

## 7. 系统架构

```
主程序 (main.py)
├── 配置管理 (src/config.py)
├── 数据获取 (src/data_fetcher.py)
├── 数据存储 (src/data_storage.py)
├── 任务调度 (src/scheduler.py)
└── 数据库 (database/)
    ├── 模型定义 (models.py)
    ├── 连接管理 (connection.py)
    └── 初始化脚本 (init_db.py)
```

## 8. 数据表说明

- `stock_info`: 股票基本信息
- `stock_daily_data`: 股票日线数据
- `stock_transaction_detail`: 股票成交明细
- `system_log`: 系统日志

## 9. 定时任务

- **每日15:30**: 完整数据采集
- **交易时间每30分钟**: 成交明细采集
- **每日09:00**: 更新股票列表

## 10. 扩展功能

系统支持以下扩展：
- 新增数据源
- 自定义指标
- 告警机制
- 数据可视化
- API接口
