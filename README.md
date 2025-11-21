# 智能桌面清理工具

基于 PyQt6 和 AI 的智能桌面文件整理工具，支持多种AI引擎，可完全离线使用。

## ✨ 核心特性

- 🤖 **多AI引擎支持**：通义千问 / 规则引擎（完全离线）
- ⚙️ **图形化配置**：无需修改代码，界面直接配置
- 📊 **智能分析**：AI理解文件内容和上下文
- 🔄 **自动降级**：AI失败时自动切换到规则引擎
- 💾 **安全备份**：操作前自动备份，防止误删
- 🎨 **现代化UI**：友好的图形界面，实时进度显示

---

## 📚 文档导航

### 🚀 快速开始
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - 用户使用指南（推荐首读）
- **[QUICK_START.md](docs/QUICK_START.md)** - 快速开始指南
- **[FIXED.md](docs/FIXED.md)** - 问题修复说明

### 📖 配置文档
- **[CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md)** - 配置参数详解
- **[README_AI_PROVIDERS.md](docs/README_AI_PROVIDERS.md)** - AI提供商使用说明

### 🔧 开发文档
- **[AI_PROVIDERS_GUIDE.md](docs/AI_PROVIDERS_GUIDE.md)** - AI提供商开发指南
- **[BATCH_PROGRESS_GUIDE.md](docs/BATCH_PROGRESS_GUIDE.md)** - 批量处理进度指南
- **[TONGYI_API_GUIDE.md](docs/TONGYI_API_GUIDE.md)** - 通义千问API指南

### 📝 更新记录
- **[CHANGELOG.md](docs/CHANGELOG.md)** - 版本更新日志

---

## 🎯 三种使用方式

### 1️⃣ 通义千问（智能分析）
需要API Key，智能程度最高
```python
# 在界面点击"⚙ 设置"，选择"通义千问"，填写API Key
```

### 2️⃣ 规则引擎（完全离线）
无需API Key，完全免费
```python
# 在界面点击"⚙ 设置"，选择"规则引擎"
```

### 3️⃣ 混合模式（推荐）
AI失败时自动降级到规则引擎
```python
# 默认已启用，无需配置
```

---

## 📦 快速安装

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行程序
```bash
python main.py
```

### 3. 配置AI引擎
程序启动后：
1. 点击右上角 **"⚙ 设置"** 按钮
2. 选择AI引擎（通义千问 或 规则引擎）
3. 如果选择通义千问，填写API Key
4. 保存设置
5. 开始使用！

**获取通义千问API Key**：[点击这里](https://dashscope.aliyun.com/)

---

## 💡 使用流程

```
1. 点击"⚙ 设置" → 配置AI引擎
2. 点击"开始扫描" → 扫描文件
3. 点击"AI分析" → 智能分析
4. 点击"执行操作" → 整理文件
```

---

## 🏗️ 项目结构

```
desktop-cleaner/
├── main.py                      # 应用入口
├── config.py                    # 全局配置
├── requirements.txt             # 依赖包
│
├── ui/                          # UI界面
│   ├── main_window.py          # 主窗口
│   └── settings_dialog.py      # 设置对话框
│
├── core/                        # 核心逻辑
│   ├── file_scanner.py         # 文件扫描
│   ├── ai_analyzer.py          # AI分析器（多提供商）
│   ├── file_manager.py         # 文件操作
│   ├── user_config.py          # 用户配置管理
│   │
│   └── ai_providers/           # AI提供商模块
│       ├── base_provider.py    # 抽象基类
│       ├── tongyi_provider.py  # 通义千问
│       ├── rule_based_provider.py  # 规则引擎
│       └── provider_factory.py # 提供商工厂
│
└── docs/                        # 文档目录
    ├── USER_GUIDE.md           # 用户使用指南
    ├── QUICK_START.md          # 快速开始指南
    ├── FIXED.md                # 问题修复说明
    ├── CONFIG_GUIDE.md         # 配置参数详解
    ├── README_AI_PROVIDERS.md  # AI提供商使用说明
    ├── AI_PROVIDERS_GUIDE.md   # AI提供商开发指南
    ├── BATCH_PROGRESS_GUIDE.md # 批量处理进度指南
    ├── TONGYI_API_GUIDE.md     # 通义千问API指南
    └── CHANGELOG.md            # 版本更新日志
```

---

## ⚙️ 主要配置

### AI提供商配置
```python
# config.py
AI_PROVIDER = 'tongyi'           # 'tongyi' 或 'rule_based'
AI_FALLBACK_TO_RULES = True      # 启用自动降级
```

### 扫描路径配置
```python
DEFAULT_SCAN_PATHS = [
    str(Path.home() / "Desktop"),    # 桌面
    str(Path.home() / "Downloads"),  # 下载文件夹
]
```

### 备份设置
```python
BACKUP_FOLDER = str(Path.home() / "Desktop" / "备份文件夹")
ENABLE_BACKUP = True  # 强烈建议开启
```

更多配置请参考：[CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md)

---

## 🎨 功能特点

### 多AI引擎支持
- ✅ 通义千问：智能分析，理解上下文
- ✅ 规则引擎：完全离线，快速分析
- ✅ 自动降级：AI失败时自动切换
- ✅ 易于扩展：可添加OpenAI、Ollama等

### 用户友好
- 🖱️ 图形化配置：无需修改代码
- 📊 实时进度：批量处理进度显示
- 💬 悬浮提示：详细信息气泡
- 🎨 现代化UI：柔和配色，舒适体验

### 安全可靠
- 💾 自动备份：删除前自动备份
- 🔄 配置持久化：设置自动保存
- ⚠️ 智能提示：操作前二次确认
- 🛡️ 权限处理：安全的文件操作

---

## 📊 AI引擎对比

| 特性 | 通义千问 | 规则引擎 |
|------|----------|----------|
| 需要API Key | ✅ | ❌ |
| 需要网络 | ✅ | ❌ |
| 智能程度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 分析速度 | 中等 | 极快 |
| 成本 | 低 | 免费 |
| 上下文理解 | ✅ | ❌ |

---

## 🔧 常见问题

### Q: 如何切换AI引擎？
A: 点击"⚙ 设置" → 选择引擎 → 保存

### Q: 没有API Key可以用吗？
A: 可以！选择"规则引擎"，完全免费离线

### Q: API Key会被上传吗？
A: 不会！API Key仅保存在本地，只用于调用通义千问API

### Q: 配置会丢失吗？
A: 不会！配置自动保存在 `~/.desktop-cleaner/user_config.json`

### Q: 规则引擎够用吗？
A: 对于简单文件分类够用，复杂场景建议用通义千问

更多问题请查看：[USER_GUIDE.md](docs/USER_GUIDE.md)

---

## 🚀 高级功能

### 自定义规则引擎参数
```python
# 在设置界面调整
旧文件阈值: 90天
临时文件阈值: 7天
```

### 批量处理配置
```python
批次大小: 10  # 每次分析的文件数
超时时间: 120秒
```

### 添加新的AI提供商
参考：[AI_PROVIDERS_GUIDE.md](docs/AI_PROVIDERS_GUIDE.md)

---

## 📝 更新日志

### v2.0.0 (2025-11-21) - 重大更新
- 🎯 AI提供商插件化架构
- ⚙️ 图形化设置界面
- 🔄 自动降级机制
- 📱 用户配置管理
- 🎨 UI优化（上下布局、柔和配色）
- 📏 文件大小改为KB精度

查看完整更新：[CHANGELOG.md](docs/CHANGELOG.md)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发指南
1. Fork 本项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- PyQt6 - 图形界面框架
- 通义千问 - AI分析引擎
- 所有贡献者

---

## 📞 获取帮助

- 📖 查看文档：[docs/](docs/)
- 🐛 报告问题：[GitHub Issues](https://github.com)
- 💬 讨论交流：[Discussions](https://github.com)

---

## ⭐ 开始使用

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行程序
python main.py

# 3. 点击"⚙ 设置"配置AI引擎

# 4. 开始智能清理！
```

祝使用愉快！🎉
