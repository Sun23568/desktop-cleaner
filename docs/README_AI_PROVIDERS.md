# 🎯 AI提供商使用说明

## 📝 概述

现在项目已经**去本土化**，不再强依赖通义千问API。你可以在以下三种方式中自由选择：

---

## 🚀 三种使用方式

### 1️⃣ 通义千问（默认，需要API Key）

**在 `config.py` 中配置：**
```python
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-your-api-key-here"
AI_FALLBACK_TO_RULES = True  # 推荐：失败时自动降级
```

### 2️⃣ 规则引擎（完全离线，不需要API Key）

**在 `config.py` 中配置：**
```python
AI_PROVIDER = 'rule_based'  # 只需要这一行！
```

### 3️⃣ 混合模式（最稳定）

**在 `config.py` 中配置：**
```python
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-your-api-key-here"
AI_FALLBACK_TO_RULES = True  # AI失败自动切换到规则引擎
```

---

## ⚙️ 完整配置说明

在 `config.py` 中，你会看到以下配置项：

```python
# ========================================
# AI 提供商配置（重要！）
# ========================================
# 可选值:
#   'tongyi'      - 通义千问（需要API Key，云端AI，智能分析）
#   'rule_based'  - 规则引擎（无需API Key，完全离线，基于规则）
AI_PROVIDER = 'tongyi'  # 默认使用通义千问

# 自动降级配置
# 当AI分析失败时，是否自动切换到规则引擎
AI_FALLBACK_TO_RULES = True

# ========================================
# 规则引擎配置（当使用 rule_based 提供商时）
# ========================================
RULE_OLD_FILE_DAYS = 90   # 多少天未修改视为旧文件
RULE_TEMP_FILE_DAYS = 7   # 临时文件多少天未修改可删除
```

---

## 🔄 快速切换

### 切换到规则引擎（完全离线）
只需要修改一行：
```python
AI_PROVIDER = 'rule_based'
```

### 切换回通义千问
```python
AI_PROVIDER = 'tongyi'
```

---

## 📊 两种方案对比

| 特性 | 通义千问 | 规则引擎 |
|------|----------|----------|
| 需要API Key | ✅ 是 | ❌ 否 |
| 需要网络 | ✅ 是 | ❌ 否 |
| 智能程度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 分析速度 | 中等 | 极快 |
| 成本 | 低 | 免费 |
| 上下文理解 | ✅ 强 | ❌ 无 |

---

## 🎓 规则引擎工作原理

规则引擎根据以下规则分类文件：

### 临时文件 (`.tmp`, `.temp`, `.cache`, `.log`)
- 7天未修改 → 建议删除
- 最近修改 → 保留

### 文档 (`.doc`, `.pdf`, `.txt`, `.xlsx`)
- 90天未修改 → 建议归档
- 最近使用 → 保留

### 图片/视频/音频
- 建议移动到专门文件夹

### 压缩包/安装包
- 长时间未使用 → 建议删除

---

## 💡 推荐配置

### 场景1: 我没有API Key
```python
AI_PROVIDER = 'rule_based'
```

### 场景2: 我需要最智能的分析
```python
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-xxxxx"
TONGYI_MODEL = "qwen-max"
```

### 场景3: 我需要高可用性
```python
AI_PROVIDER = 'tongyi'
AI_FALLBACK_TO_RULES = True  # 推荐！
AI_MAX_RETRIES = 5
```

### 场景4: 内网环境/离线使用
```python
AI_PROVIDER = 'rule_based'
```

---

## 🔧 故障排查

### Q: 提示 "通义千问API Key未配置"
**A:** 检查 `config.py` 中的 `TONGYI_API_KEY` 是否填写

### Q: 想完全不依赖外部API
**A:** 设置 `AI_PROVIDER = 'rule_based'`

### Q: AI调用失败了怎么办
**A:** 设置 `AI_FALLBACK_TO_RULES = True`，会自动降级到规则引擎

---

## 📚 更多文档

- 详细开发指南：`docs/AI_PROVIDERS_GUIDE.md`
- 快速开始：`docs/QUICK_START.md`
- 配置说明：`docs/CONFIG_GUIDE.md`

---

## ✨ 架构优势

✅ **灵活切换** - 一行配置即可切换
✅ **完全离线** - 规则引擎无需网络
✅ **自动降级** - AI失败时自动fallback
✅ **易于扩展** - 可轻松添加OpenAI、Ollama等
✅ **零成本选项** - 规则引擎完全免费

---

## 🎉 开始使用

1. 打开 `config.py`
2. 找到 `AI_PROVIDER` 配置项
3. 选择你想要的提供商
4. 保存并运行 `python main.py`

就这么简单！
