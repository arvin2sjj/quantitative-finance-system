# 数据源配置指南

## 概述

本系统支持多种数据源，包括akshare和tushare，并实现了智能降级机制，确保数据获取的稳定性。

## 支持的数据源

### 1. AKShare
- **类型**: 免费开源数据源
- **特点**: 无需注册，数据丰富，网络稳定
- **适用场景**: 日常数据采集，批量导入

### 2. Tushare
- **类型**: 专业金融数据服务
- **特点**: 数据质量高，更新及时，需要token
- **适用场景**: 专业量化分析，高频数据需求

## 配置方法

### 1. 修改配置文件

编辑 `config.env` 文件：

```bash
# 数据源配置
DATA_SOURCE=tushare  # 可选: akshare, tushare

# Tushare配置（如果使用tushare）
TUSHARE_TOKEN=your_tushare_token_here
```

### 2. 更新环境变量

```bash
cp config.env .env
```

## 降级机制

系统实现了智能降级机制，确保数据获取的稳定性：

### Tushare数据源降级流程
1. **Tushare Pro API** → 尝试使用最新的专业API
2. **Tushare旧版API** → 如果Pro API失败，尝试旧版API
3. **AKShare** → 如果tushare都失败，降级到akshare

### 降级触发条件
- Token权限不足
- 网络连接问题
- API服务不可用
- 数据获取超时

## 使用示例

### 1. 使用AKShare数据源

```bash
# 配置
DATA_SOURCE=akshare

# 导入股票列表
python batch_import.py --stock-list

# 导入日线数据
python batch_import.py --symbols 000001 --start-date 20240901 --end-date 20240906 --data-types daily
```

### 2. 使用Tushare数据源

```bash
# 配置
DATA_SOURCE=tushare
TUSHARE_TOKEN=your_token_here

# 导入股票列表（会自动降级到akshare如果tushare失败）
python batch_import.py --stock-list

# 导入日线数据（会自动降级到akshare如果tushare失败）
python batch_import.py --symbols 000001 --start-date 20240901 --end-date 20240906 --data-types daily
```

## 数据源对比

| 特性 | AKShare | Tushare |
|------|---------|---------|
| 费用 | 免费 | 需要积分/付费 |
| 注册 | 无需注册 | 需要注册获取token |
| 数据质量 | 良好 | 优秀 |
| 更新频率 | 实时 | 实时 |
| 网络稳定性 | 稳定 | 稳定 |
| 数据完整性 | 完整 | 完整 |
| 技术支持 | 社区支持 | 官方支持 |

## 故障排除

### 1. Tushare Token问题

**问题**: `抱歉，您没有接口访问权限`

**解决方案**:
- 检查token是否正确
- 确认token有足够的积分
- 访问 [tushare.pro](https://tushare.pro) 查看权限详情

### 2. 网络连接问题

**问题**: `Connection aborted` 或 `获取失败，请检查网络`

**解决方案**:
- 检查网络连接
- 等待网络恢复
- 系统会自动降级到其他数据源

### 3. 数据格式问题

**问题**: 数据列数不匹配或列名错误

**解决方案**:
- 系统已内置列名映射
- 会自动处理不同数据源的格式差异
- 查看日志了解具体处理过程

## 最佳实践

### 1. 数据源选择建议

- **开发测试**: 使用akshare，免费且稳定
- **生产环境**: 根据需求选择，建议配置降级机制
- **高频交易**: 使用tushare，数据质量更高

### 2. 配置建议

- 始终配置降级机制
- 定期检查token状态
- 监控数据获取成功率
- 设置合理的重试次数

### 3. 性能优化

- 批量获取数据时添加适当延时
- 使用缓存减少重复请求
- 监控API调用频率限制

## 日志监控

系统会记录详细的数据获取日志：

```
2025-09-07 09:32:26 | INFO | 初始化数据获取器，数据源: tushare
2025-09-07 09:32:26 | WARNING | Tushare Pro API获取股票列表失败，尝试旧版API
2025-09-07 09:32:26 | WARNING | Tushare旧版API也失败，降级使用akshare
2025-09-07 09:32:36 | INFO | 使用akshare成功获取股票列表，共 5427 只股票
```

## 更新日志

- **2025-09-07**: 添加tushare数据源支持
- **2025-09-07**: 实现智能降级机制
- **2025-09-07**: 支持tushare Pro API和旧版API
- **2025-09-07**: 完善错误处理和日志记录

## 联系支持

如有问题，请通过以下方式联系：
- GitHub Issues
- Email: arvin553263759@hotmail.com
- 查看系统日志文件: `logs/quantitative_finance.log`
