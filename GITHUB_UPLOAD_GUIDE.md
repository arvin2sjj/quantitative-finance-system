# GitHub上传指南

## 步骤1: 在GitHub上创建新仓库

1. 访问 [GitHub.com](https://github.com) 并登录您的账户
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `quantitative-finance-system`
   - **Description**: `量化金融系统 - 支持批量导入沪深股票历史数据`
   - **Visibility**: 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（因为我们已经有了）
4. 点击 "Create repository"

## 步骤2: 上传代码到GitHub

### 方法1: 使用提供的脚本（推荐）

```bash
# 替换 yourusername 为您的GitHub用户名
./upload_to_github.sh yourusername
```

### 方法2: 手动执行命令

```bash
# 1. 添加远程仓库（替换yourusername为您的GitHub用户名）
git remote add origin https://github.com/yourusername/quantitative-finance-system.git

# 2. 推送代码到GitHub
git branch -M main
git push -u origin main
```

## 步骤3: 验证上传

1. 访问您的GitHub仓库页面
2. 确认所有文件都已上传
3. 检查README.md是否正确显示

## 仓库信息

- **仓库名称**: quantitative-finance-system
- **描述**: 量化金融系统 - 支持批量导入沪深股票历史数据
- **主要功能**:
  - 自动数据采集
  - 批量导入历史数据
  - MySQL数据库存储
  - 智能任务调度
  - 完整的日志系统

## 文件结构

```
quantitative-finance-system/
├── src/                    # 核心模块
│   ├── data_fetcher.py    # 数据获取模块
│   ├── data_storage.py    # 数据存储模块
│   ├── scheduler.py       # 任务调度模块
│   ├── batch_importer.py  # 批量导入模块
│   └── config.py          # 配置管理模块
├── database/              # 数据库模块
├── logs/                  # 日志目录
├── main.py               # 主程序入口
├── batch_import.py       # 批量导入工具
├── requirements.txt      # 依赖包
├── README.md             # 项目说明
├── BATCH_IMPORT_GUIDE.md # 批量导入使用指南
└── upload_to_github.sh   # GitHub上传脚本
```

## 注意事项

1. 确保您有GitHub账户
2. 确保您有推送权限
3. 如果遇到认证问题，可能需要配置SSH密钥或使用Personal Access Token
4. 敏感信息（如数据库密码）已通过.gitignore排除

## 后续操作

上传成功后，您可以：

1. 在GitHub上查看代码
2. 创建Issues来跟踪问题
3. 创建Pull Requests来贡献代码
4. 设置GitHub Actions进行自动化测试
5. 邀请其他开发者协作

## 故障排除

### 如果遇到认证问题：

1. **使用Personal Access Token**:
   ```bash
   git remote set-url origin https://yourusername:your_token@github.com/yourusername/quantitative-finance-system.git
   ```

2. **配置SSH密钥**:
   ```bash
   git remote set-url origin git@github.com:yourusername/quantitative-finance-system.git
   ```

### 如果遇到推送问题：

```bash
# 强制推送（谨慎使用）
git push -f origin main
```

## 联系信息

如有问题，请通过以下方式联系：
- GitHub Issues
- Email: arvin553263759@hotmail.com
