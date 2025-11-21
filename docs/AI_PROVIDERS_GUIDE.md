# AI提供商架构指南

## 📋 概述

本项目采用**插件化AI提供商架构**，支持多种AI服务和本地分析引擎。你可以轻松切换不同的AI提供商，或添加自己的实现。

## 🎯 设计理念

- **解耦**: AI逻辑与业务逻辑分离
- **可扩展**: 轻松添加新的AI提供商
- **容错**: 支持自动降级到规则引擎
- **灵活**: 配置化切换，无需修改代码

## 🏗️ 架构图

```
AIAnalyzer (统一入口)
    ↓
AIProviderFactory (工厂类)
    ↓
AIProvider (抽象基类)
    ├── TongyiProvider (通义千问)
    ├── RuleBasedProvider (规则引擎)
    ├── OpenAIProvider (OpenAI) - 可扩展
    ├── OllamaProvider (本地模型) - 可扩展
    └── 自定义Provider...
```

## 📦 已支持的提供商

### 1. 通义千问 (tongyi)
- **类型**: 云端AI
- **需要**: API Key
- **特点**: 智能分析，理解上下文
- **配置**:
```python
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "your-api-key"
TONGYI_MODEL = "qwen-plus"
```

### 2. 规则引擎 (rule_based)
- **类型**: 本地规则
- **需要**: 无
- **特点**: 完全离线，快速，确定性
- **配置**:
```python
AI_PROVIDER = 'rule_based'
RULE_OLD_FILE_DAYS = 90
RULE_TEMP_FILE_DAYS = 7
```

## 🚀 快速开始

### 1. 使用通义千问

在 `config.py` 中:
```python
AI_PROVIDER = 'tongyi'
TONGYI_API_KEY = "sk-xxxxx"
```

### 2. 切换到规则引擎

在 `config.py` 中:
```python
AI_PROVIDER = 'rule_based'
```

### 3. 启用自动降级

当AI失败时自动切换到规则引擎:
```python
AI_FALLBACK_TO_RULES = True
```

## 🔧 添加新的AI提供商

### 步骤1: 创建提供商类

在 `core/ai_providers/` 创建新文件，例如 `openai_provider.py`:

```python
from .base_provider import AIProvider
from typing import List, Dict

class OpenAIProvider(AIProvider):
    """OpenAI提供商"""

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = self.config.get('openai_api_key', '')
        self.model = self.config.get('openai_model', 'gpt-4')

    def get_provider_name(self) -> str:
        return "OpenAI (GPT)"

    def is_available(self) -> bool:
        return bool(self.api_key)

    def analyze_files(self, files: List[Dict]) -> Dict:
        # 实现OpenAI API调用
        # ...
        return {
            'suggestions': [...],
            'categories': {...}
        }
```

### 步骤2: 注册提供商

在 `provider_factory.py` 中:
```python
from .openai_provider import OpenAIProvider

PROVIDERS = {
    'tongyi': TongyiProvider,
    'rule_based': RuleBasedProvider,
    'openai': OpenAIProvider,  # 添加这行
}
```

### 步骤3: 更新配置

在 `config.py` 中:
```python
AI_PROVIDER = 'openai'
OPENAI_API_KEY = "sk-xxxxx"
OPENAI_MODEL = "gpt-4"
```

## 📝 提供商接口规范

所有提供商必须继承 `AIProvider` 并实现以下方法:

### 必须实现的方法

#### 1. `get_provider_name()` -> str
返回提供商的显示名称

#### 2. `is_available()` -> bool
检查提供商是否可用（如API Key是否配置）

#### 3. `analyze_files(files: List[Dict])` -> Dict
分析文件列表并返回建议

**输入格式**:
```python
files = [
    {
        'name': 'example.pdf',
        'path': '/home/user/Desktop/example.pdf',
        'extension': '.pdf',
        'size_kb': 1024.5,
        'size_mb': 1.0,
        'modified_time': '2025-11-20 10:30:00',
        'created_time': '2025-11-01 09:00:00'
    },
    ...
]
```

**返回格式**:
```python
{
    'suggestions': [
        {
            'file_path': '/home/user/Desktop/example.pdf',
            'action': 'keep',  # 'delete', 'move', 'keep'
            'reason': '最近使用的文档',
            'category': '文档',
            'confidence': 0.9  # 0-1之间
        },
        ...
    ],
    'categories': {
        '临时文件': ['file1.tmp', 'file2.tmp'],
        '文档': ['example.pdf'],
        ...
    }
}
```

## 🎨 本地模型示例 (Ollama)

如果要使用本地大模型（如通过Ollama）:

```python
# core/ai_providers/ollama_provider.py
import requests
from .base_provider import AIProvider

class OllamaProvider(AIProvider):
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.base_url = self.config.get('ollama_url', 'http://localhost:11434')
        self.model = self.config.get('ollama_model', 'qwen2:7b')

    def get_provider_name(self) -> str:
        return f"Ollama ({self.model})"

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def analyze_files(self, files: List[Dict]) -> Dict:
        prompt = self._build_prompt(files)

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )

        # 解析响应...
        return result
```

配置:
```python
AI_PROVIDER = 'ollama'
OLLAMA_URL = 'http://localhost:11434'
OLLAMA_MODEL = 'qwen2:7b'
```

## 🛡️ 错误处理

### 自动降级
```python
# config.py
AI_FALLBACK_TO_RULES = True  # AI失败时自动切换到规则引擎
```

### 手动处理
```python
try:
    analyzer = AIAnalyzer(provider_type='tongyi')
    result = analyzer.analyze_files(files)
except Exception as e:
    # 降级到规则引擎
    analyzer = AIAnalyzer(provider_type='rule_based')
    result = analyzer.analyze_files(files)
```

## 📊 性能对比

| 提供商 | 速度 | 准确度 | 成本 | 离线 |
|--------|------|--------|------|------|
| 通义千问 | 中等 | 高 | 低 | ❌ |
| 规则引擎 | 极快 | 中等 | 无 | ✅ |
| OpenAI | 中等 | 很高 | 高 | ❌ |
| Ollama | 快 | 高 | 无 | ✅ |

## 💡 最佳实践

1. **开发环境**: 使用规则引擎快速测试
2. **生产环境**: 使用云端AI + 规则引擎fallback
3. **离线环境**: 使用Ollama或规则引擎
4. **成本优化**: 先用规则引擎过滤，再用AI精细分析

## 🔍 调试技巧

### 查看当前使用的提供商
```python
analyzer = AIAnalyzer()
print(f"当前提供商: {analyzer.provider.get_provider_name()}")
print(f"是否可用: {analyzer.provider.is_available()}")
```

### 强制使用特定提供商
```python
# 测试规则引擎
analyzer = AIAnalyzer(provider_type='rule_based')

# 测试通义千问
analyzer = AIAnalyzer(provider_type='tongyi')
```

### 启用详细日志
```python
# config.py
ENABLE_DETAIL_LOG = True
LOG_REQUEST_PARAMS = True
LOG_RESPONSE_CONTENT = True
```

## 📚 扩展阅读

- [通义千问API文档](https://help.aliyun.com/zh/dashscope/)
- [OpenAI API文档](https://platform.openai.com/docs)
- [Ollama文档](https://ollama.ai/docs)

## ❓ 常见问题

### Q: 如何完全不依赖外部AI？
A: 设置 `AI_PROVIDER = 'rule_based'`

### Q: AI失败了怎么办？
A: 启用 `AI_FALLBACK_TO_RULES = True`，系统会自动降级

### Q: 可以同时使用多个AI吗？
A: 可以，自己实现一个MultiProvider类，内部调用多个提供商并合并结果

### Q: 规则引擎够用吗？
A: 对于简单场景（按扩展名分类、按时间清理）够用，复杂场景建议用AI

## 🤝 贡献

欢迎提交新的AI提供商实现！提交PR时请包含:
1. 提供商实现代码
2. 配置示例
3. 使用文档
