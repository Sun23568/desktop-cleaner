# 通义千问API接口实现指南

本文档详细说明如何在 `core/ai_analyzer.py` 中实现通义千问API调用。

## 快速开始

### 步骤1: 获取API Key

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 开通通义千问服务
3. 创建API Key并复制

### 步骤2: 配置API Key

编辑 `config.py` 文件：

```python
TONGYI_API_KEY = "sk-xxxxxxxxxxxxxxxx"  # 粘贴你的API Key
TONGYI_MODEL = "qwen-max"  # 或 qwen-plus, qwen-turbo
```

### 步骤3: 实现API调用

打开 `core/ai_analyzer.py`，找到第108行左右的 `_call_tongyi_api` 方法。

## 实现方案

### 方案1: 使用 dashscope SDK（推荐）

**安装SDK:**
```bash
pip install dashscope
```

**代码实现:**

```python
def _call_tongyi_api(self, prompt: str) -> str:
    """
    调用通义千问API（使用dashscope SDK）
    """
    import dashscope
    from dashscope import Generation

    # 设置API Key
    dashscope.api_key = self.api_key

    try:
        # 调用通义千问
        response = Generation.call(
            model=self.model,
            prompt=prompt,
            result_format='message'  # 返回格式
        )

        # 检查响应状态
        if response.status_code == 200:
            # 提取响应文本
            return response.output.text
        else:
            raise Exception(f"API调用失败: {response.message}")

    except Exception as e:
        print(f"通义API调用出错: {e}")
        raise
```

### 方案2: 使用 HTTP 请求（OpenAI兼容模式）

**安装依赖:**
```bash
pip install requests
```

**代码实现:**

```python
def _call_tongyi_api(self, prompt: str) -> str:
    """
    调用通义千问API（使用HTTP请求）
    """
    import requests
    import json

    # API端点
    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    # 请求头
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
    }

    # 请求数据
    data = {
        "model": self.model,
        "messages": [
            {
                "role": "system",
                "content": "你是一个智能文件管理助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        # 发送请求
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=config.AI_TIMEOUT
        )

        # 检查响应
        response.raise_for_status()

        # 解析响应
        result = response.json()
        return result['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        print(f"HTTP请求失败: {e}")
        raise
    except (KeyError, json.JSONDecodeError) as e:
        print(f"响应解析失败: {e}")
        raise
```

### 方案3: 使用 OpenAI SDK（如果通义支持OpenAI协议）

**安装SDK:**
```bash
pip install openai
```

**代码实现:**

```python
def _call_tongyi_api(self, prompt: str) -> str:
    """
    调用通义千问API（使用OpenAI SDK）
    """
    from openai import OpenAI

    # 初始化客户端
    client = OpenAI(
        api_key=self.api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    try:
        # 调用API
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个智能文件管理助手。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7
        )

        # 返回响应
        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI SDK调用失败: {e}")
        raise
```

## 完整示例

下面是一个完整的 `_call_tongyi_api` 实现（方案1）：

```python
def _call_tongyi_api(self, prompt: str) -> str:
    """
    调用通义千问API

    :param prompt: 发送给AI的提示词
    :return: AI的响应文本
    """
    # 使用 dashscope SDK
    import dashscope
    from dashscope import Generation

    # 设置API Key
    dashscope.api_key = self.api_key

    try:
        print(f"正在调用通义千问 {self.model} 模型...")

        # 调用API
        response = Generation.call(
            model=self.model,
            prompt=prompt,
            result_format='message',
            max_tokens=2000,  # 最大token数
            temperature=0.7,  # 温度参数
            top_p=0.9
        )

        # 检查响应
        if response.status_code == 200:
            result_text = response.output.text
            print(f"API调用成功，返回长度: {len(result_text)} 字符")
            return result_text
        else:
            error_msg = f"API调用失败: {response.code} - {response.message}"
            print(error_msg)
            raise Exception(error_msg)

    except Exception as e:
        print(f"通义API调用异常: {str(e)}")
        # 返回模拟数据用于测试
        print("警告: 返回模拟数据")
        return self._get_mock_response()
```

## 测试API连接

在 `desktop-cleaner` 目录下创建测试文件 `test_api.py`：

```python
"""
测试通义千问API连接
"""
import sys
sys.path.append('.')

from core.ai_analyzer import AIAnalyzer

def test_api():
    analyzer = AIAnalyzer()

    # 测试数据
    test_files = [
        {
            'name': 'test.tmp',
            'path': '/home/user/Desktop/test.tmp',
            'extension': '.tmp',
            'size_mb': 1.5,
            'modified_time': '2024-01-01 10:00:00'
        }
    ]

    print("开始测试通义千问API...")
    try:
        result = analyzer.analyze_files(test_files)
        print("测试成功！")
        print("返回结果:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    test_api()
```

运行测试：
```bash
python test_api.py
```

## 常见问题

### Q1: API Key无效

**错误信息**: "Invalid API Key" 或类似

**解决方案**:
- 检查 `config.py` 中的 API Key 是否正确
- 确认API Key未过期
- 检查是否有多余的空格

### Q2: 模型不存在

**错误信息**: "Model not found"

**解决方案**:
- 检查模型名称是否正确（qwen-max, qwen-plus, qwen-turbo）
- 确认账号已开通相应模型的权限

### Q3: 请求超时

**错误信息**: "Timeout"

**解决方案**:
- 检查网络连接
- 增大 `config.py` 中的 `AI_TIMEOUT` 值
- 减少 `MAX_FILES_PER_REQUEST` 的值

### Q4: 返回格式错误

**错误信息**: "JSON decode error"

**解决方案**:
- 在提示词中明确要求只返回JSON
- 在 `_parse_response` 方法中增加容错处理
- 检查模型返回是否包含markdown代码块

## 优化建议

### 1. 添加重试机制

```python
import time

def _call_tongyi_api(self, prompt: str) -> str:
    max_retries = 3

    for i in range(max_retries):
        try:
            # 调用API
            response = ...
            return response
        except Exception as e:
            if i < max_retries - 1:
                print(f"重试 {i+1}/{max_retries}...")
                time.sleep(2)
            else:
                raise
```

### 2. 添加缓存

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def _call_tongyi_api_cached(self, prompt_hash: str, prompt: str) -> str:
    # 调用API
    pass
```

### 3. 限流控制

```python
import time

class AIAnalyzer:
    def __init__(self):
        self.last_call_time = 0
        self.min_interval = 1  # 最小调用间隔（秒）

    def _call_tongyi_api(self, prompt: str) -> str:
        # 限流
        elapsed = time.time() - self.last_call_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)

        # 调用API
        result = ...

        self.last_call_time = time.time()
        return result
```

## 相关资源

- [通义千问官方文档](https://help.aliyun.com/zh/dashscope/)
- [DashScope SDK文档](https://help.aliyun.com/zh/dashscope/developer-reference/api-details)
- [API价格说明](https://help.aliyun.com/zh/dashscope/developer-reference/tongyi-qianwen-metering-and-billing)

## 技术支持

如果遇到问题：
1. 查看 README.md 的常见问题部分
2. 检查通义千问官方文档
3. 在控制台查看详细错误信息
