# 配置指南

本文档详细说明 `config.py` 中的各项配置参数。

## AI 分析配置

### `MAX_FILES_PER_REQUEST`
**默认值**: `10`
**说明**: 每次发送给AI的最大文件数量

**调整建议**:
- 如果经常超时，减小到 `5-8`
- 如果响应很快，可以增加到 `15-20`
- 建议范围: `5-20`

**示例**:
```python
MAX_FILES_PER_REQUEST = 10  # 每批10个文件
```

### `AI_TIMEOUT`
**默认值**: `120`
**说明**: API请求超时时间（秒）

**调整建议**:
- 网络较慢时增加到 `180-300`
- 网络很好时可以减少到 `60-90`
- 建议范围: `60-300`

**示例**:
```python
AI_TIMEOUT = 120  # 2分钟超时
```

### `AI_MAX_RETRIES`
**默认值**: `3`
**说明**: API调用失败时的最大重试次数

**调整建议**:
- 网络不稳定时增加到 `5`
- 网络稳定时保持 `2-3`

**示例**:
```python
AI_MAX_RETRIES = 3  # 最多重试3次
```

### `AI_RETRY_DELAY`
**默认值**: `5`
**说明**: 重试间隔时间（秒）

**说明**:
- 第1次重试等待: 5秒
- 第2次重试等待: 10秒
- 第3次重试等待: 15秒
- 以此类推...

**示例**:
```python
AI_RETRY_DELAY = 5  # 每次重试递增5秒
```

## 日志配置

### `ENABLE_DETAIL_LOG`
**默认值**: `True`
**说明**: 是否启用详细日志（包括请求和响应内容）

**使用场景**:
- `True`: 调试时使用，可以看到完整的请求和响应
- `False`: 生产环境使用，减少日志输出

**示例**:
```python
ENABLE_DETAIL_LOG = True  # 开启详细日志
```

### `LOG_REQUEST_PARAMS`
**默认值**: `True`
**说明**: 是否记录请求参数

**输出内容**:
- API URL
- 使用的模型
- 超时设置
- 提示词长度和内容预览
- 完整请求体

**示例**:
```python
LOG_REQUEST_PARAMS = True  # 记录请求参数
```

### `LOG_RESPONSE_CONTENT`
**默认值**: `True`
**说明**: 是否记录响应内容

**输出内容**:
- HTTP状态码
- Token使用情况（输入/输出/总计）
- AI响应内容预览
- 完整响应（如果不太长）

**示例**:
```python
LOG_RESPONSE_CONTENT = True  # 记录响应内容
```

## 日志输出示例

### 开启详细日志时的输出

```
================================================================================
📦 批量处理模式
   总文件数: 71
   每批大小: 10 (可在config.py中调整MAX_FILES_PER_REQUEST)
   分批数量: 8
================================================================================

▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶
📋 处理批次 1/8
   文件范围: 1 - 10
   本批文件数: 10
   文件列表:
      1. document.pdf (2.5MB)
      2. image.jpg (1.2MB)
      3. video.mp4 (50.3MB)
      4. setup.exe (120.5MB)
      5. notes.txt (0.01MB)
      ... 还有 5 个文件
▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶▶

🔄 开始分析批次 1/8...

================================================================================
📡 通义千问API调用 - 尝试 1/3
================================================================================

📤 请求参数:
   URL: https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
   模型: qwen-max
   超时设置: 120秒
   提示词长度: 2456 字符

   消息内容:
   你是一个智能文件管理助手。请分析以下桌面和下载文件夹中的文件...

   完整请求体:
   {
     "model": "qwen-max",
     "messages": [
       {
         "role": "user",
         "content": "你是一个智能文件管理助手..."
       }
     ]
   }...

✅ API调用成功！
⏱️  耗时: 5.23秒
📊 响应长度: 1234 字符

📥 响应内容:
   HTTP状态码: 200

   Token使用:
      输入tokens: 856
      输出tokens: 425
      总计tokens: 1281

   AI响应内容（前500字符）:
   {
     "suggestions": [
       {
         "file_path": "/home/user/Desktop/document.pdf",
         "action": "keep",
         "reason": "重要文档",
         ...

================================================================================

✅ 批次 1 解析成功，获得 10 条建议

✔️  批次 1 完成，获得 10 条建议
```

### 关闭详细日志时的输出

设置:
```python
ENABLE_DETAIL_LOG = False
# 或
LOG_REQUEST_PARAMS = False
LOG_RESPONSE_CONTENT = False
```

输出:
```
📦 批量处理模式
   总文件数: 71
   每批大小: 10
   分批数量: 8

📋 处理批次 1/8
🔄 开始分析批次 1/8...
✅ API调用成功！
✔️  批次 1 完成，获得 10 条建议
```

## 性能调优建议

### 场景1: 文件很多（100+），处理很慢

```python
MAX_FILES_PER_REQUEST = 5   # 减小批次
AI_TIMEOUT = 180            # 增加超时
```

### 场景2: 经常超时

```python
MAX_FILES_PER_REQUEST = 5   # 减小批次
AI_TIMEOUT = 240            # 增加超时
AI_MAX_RETRIES = 5          # 增加重试次数
AI_RETRY_DELAY = 10         # 增加重试间隔
```

### 场景3: 网络很好，想加快处理

```python
MAX_FILES_PER_REQUEST = 20  # 增大批次
AI_TIMEOUT = 60             # 减少超时
```

### 场景4: 调试问题

```python
ENABLE_DETAIL_LOG = True
LOG_REQUEST_PARAMS = True
LOG_RESPONSE_CONTENT = True
```

### 场景5: 生产使用，减少日志

```python
ENABLE_DETAIL_LOG = False
LOG_REQUEST_PARAMS = False
LOG_RESPONSE_CONTENT = False
```

## 其他配置

### 扫描路径
```python
DEFAULT_SCAN_PATHS = [
    str(Path.home() / "Desktop"),    # 桌面
    str(Path.home() / "Downloads"),  # 下载文件夹
    "D:/MyFiles",                    # 自定义路径
]
```

### 忽略规则
```python
IGNORE_EXTENSIONS = [
    '.ini', '.sys', '.dll',  # 系统文件
    '.tmp', '.cache',         # 临时文件
]

IGNORE_FOLDERS = [
    '$RECYCLE.BIN',
    'System Volume Information',
    '.git',
    'node_modules',
]
```

### 备份配置
```python
BACKUP_FOLDER = str(Path.home() / "Desktop" / "备份文件夹")
ENABLE_BACKUP = True  # 删除前是否备份
```

## 快速参考

| 配置项 | 默认值 | 用途 | 调整建议 |
|--------|--------|------|----------|
| `MAX_FILES_PER_REQUEST` | 10 | 批次大小 | 超时减小，快速增大 |
| `AI_TIMEOUT` | 120 | 超时时间(秒) | 网络慢增大，快减小 |
| `AI_MAX_RETRIES` | 3 | 重试次数 | 不稳定增大 |
| `AI_RETRY_DELAY` | 5 | 重试间隔(秒) | 可保持默认 |
| `ENABLE_DETAIL_LOG` | True | 详细日志 | 调试True，生产False |
| `LOG_REQUEST_PARAMS` | True | 请求日志 | 调试True，生产False |
| `LOG_RESPONSE_CONTENT` | True | 响应日志 | 调试True，生产False |

## 注意事项

1. **批次大小与超时的关系**: 批次越大，API处理时间越长，需要更长的超时时间
2. **Token消耗**: 批次越大，单次请求消耗的Token越多，成本越高
3. **日志大小**: 开启详细日志会产生大量输出，在PowerShell中可能影响可读性
4. **重试策略**: 过多的重试会增加总耗时，需要权衡

## 推荐配置

### 标准配置（推荐）
```python
MAX_FILES_PER_REQUEST = 10
AI_TIMEOUT = 120
AI_MAX_RETRIES = 3
AI_RETRY_DELAY = 5
ENABLE_DETAIL_LOG = True
LOG_REQUEST_PARAMS = True
LOG_RESPONSE_CONTENT = True
```

### 快速配置（网络好）
```python
MAX_FILES_PER_REQUEST = 15
AI_TIMEOUT = 90
AI_MAX_RETRIES = 2
AI_RETRY_DELAY = 3
ENABLE_DETAIL_LOG = False
```

### 稳定配置（网络差）
```python
MAX_FILES_PER_REQUEST = 5
AI_TIMEOUT = 180
AI_MAX_RETRIES = 5
AI_RETRY_DELAY = 10
ENABLE_DETAIL_LOG = True
```
