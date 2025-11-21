# 🚀 快速开始指南

## 📋 三种使用方式

### 1️⃣ 方式一：通义千问（推荐）

**特点**: 智能分析，理解上下文

**步骤**:
1. 获取通义千问API Key（[申请地址](https://dashscope.aliyun.com/)）
2. 修改 `config.py`:
```python
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-your-api-key-here"
TONGYI_MODEL = "qwen-plus"
```
3. 运行程序：
```bash
python main.py
```

**适用场景**: 需要智能判断、复杂场景

---

### 2️⃣ 方式二：规则引擎（完全离线）

**特点**: 不需要API Key，完全离线，快速

**步骤**:
1. 修改 `config.py`:
```python
AI_PROVIDER = 'rule_based'
```
2. 运行程序：
```bash
python main.py
```

**适用场景**:
- 没有API Key
- 需要完全离线运行
- 简单的文件分类需求

---

### 3️⃣ 方式三：混合模式（最稳定）

**特点**: AI失败时自动降级到规则引擎

**步骤**:
1. 修改 `config.py`:
```python
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-your-api-key-here"
AI_FALLBACK_TO_RULES = True  # 启用自动降级
```
2. 运行程序：
```bash
python main.py
```

**适用场景**: 生产环境，需要高可用性

---

## 🎛️ 配置说明

### 基础配置

```python
# config.py

# 选择AI提供商
AI_PROVIDER = 'tongyi'  # 'tongyi' 或 'rule_based'

# 通义千问配置（如果使用）
TONGYI_API_KEY = "sk-xxxxx"
TONGYI_MODEL = "qwen-plus"

# 自动降级配置
AI_FALLBACK_TO_RULES = True
```

### 规则引擎配置

```python
# 多少天未修改算作旧文件
RULE_OLD_FILE_DAYS = 90

# 临时文件多少天未修改可删除
RULE_TEMP_FILE_DAYS = 7
```

### 扫描路径配置

```python
DEFAULT_SCAN_PATHS = [
    str(Path.home() / "Desktop"),     # 桌面
    str(Path.home() / "Downloads"),   # 下载
]
```

---

## 💡 常见场景

### 场景1: 我没有API Key
```python
# config.py
AI_PROVIDER = 'rule_based'
```
使用规则引擎，完全免费

### 场景2: 我想要最智能的分析
```python
# config.py
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-xxxxx"
TONGYI_MODEL = "qwen-max"  # 使用最强模型
```

### 场景3: 我需要稳定性
```python
# config.py
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-xxxxx"
AI_FALLBACK_TO_RULES = True  # AI失败自动降级
AI_MAX_RETRIES = 5            # 增加重试次数
```

### 场景4: 我在内网环境
```python
# config.py
AI_PROVIDER = 'rule_based'  # 完全离线
```

---

## 🔍 功能对比

| 功能 | 通义千问 | 规则引擎 |
|------|----------|----------|
| 需要网络 | ✅ | ❌ |
| 需要API Key | ✅ | ❌ |
| 智能程度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 分析速度 | 中等 | 极快 |
| 成本 | 低 | 免费 |
| 准确率 | 很高 | 较高 |
| 上下文理解 | ✅ | ❌ |

---

## 📊 规则引擎分类规则

规则引擎基于以下规则分析文件:

### 临时文件
- 扩展名: `.tmp`, `.temp`, `.cache`, `.log`, `.bak`, `.old`
- 操作: 7天未修改则删除

### 文档
- 扩展名: `.doc`, `.docx`, `.pdf`, `.txt`, `.xlsx` 等
- 操作: 90天未修改建议归档

### 图片/视频/音频
- 图片: `.jpg`, `.png`, `.gif` 等
- 视频: `.mp4`, `.avi`, `.mkv` 等
- 音频: `.mp3`, `.wav`, `.flac` 等
- 操作: 建议移动到专门文件夹

### 压缩包
- 扩展名: `.zip`, `.rar`, `.7z` 等
- 操作: 90天未修改可删除

### 安装包
- 扩展名: `.exe`, `.msi`, `.dmg` 等
- 操作: 30天未使用建议删除

---

## 🛠️ 故障排查

### 问题1: 通义千问API调用失败
**解决方案**:
1. 检查API Key是否正确
2. 检查网络连接
3. 启用自动降级:
```python
AI_FALLBACK_TO_RULES = True
```

### 问题2: 分析结果不理想
**解决方案（通义千问）**:
```python
# 使用更强的模型
TONGYI_MODEL = "qwen-max"
```

**解决方案（规则引擎）**:
```python
# 调整规则参数
RULE_OLD_FILE_DAYS = 60    # 降低阈值
RULE_TEMP_FILE_DAYS = 3    # 更激进地清理
```

### 问题3: 处理速度慢
**解决方案**:
```python
# 方案1: 切换到规则引擎
AI_PROVIDER = 'rule_based'

# 方案2: 调整批次大小
MAX_FILES_PER_REQUEST = 20  # 增大批次
```

---

## 🎯 最佳实践

### 开发/测试
```python
AI_PROVIDER = 'rule_based'  # 快速测试
```

### 日常使用
```python
AI_PROVIDER = 'tongyi'
AI_FALLBACK_TO_RULES = True
```

### 生产部署
```python
AI_PROVIDER = 'tongyi'
TONGYI_MODEL = "qwen-plus"
AI_FALLBACK_TO_RULES = True
AI_MAX_RETRIES = 5
ENABLE_BACKUP = True  # 启用备份
```

---

## 📚 下一步

- 🔧 了解如何[添加新的AI提供商](AI_PROVIDERS_GUIDE.md)
- 📖 查看[完整配置说明](CONFIG_GUIDE.md)
- 📝 阅读[更新日志](CHANGELOG.md)

---

## ❓ 需要帮助?

遇到问题？请查看:
1. [配置指南](CONFIG_GUIDE.md)
2. [AI提供商指南](AI_PROVIDERS_GUIDE.md)
3. [常见问题](../README.md#常见问题)
