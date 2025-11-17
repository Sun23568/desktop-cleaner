# 智能桌面清理工具

基于 PyQt6 和通义千问大模型的智能桌面文件整理工具。

## 功能特点

- 自动扫描桌面和下载文件夹
- AI智能分析文件，给出整理建议
- 支持文件删除、移动、分类
- 自动备份功能，防止误删
- 友好的图形界面

## 项目结构

```
desktop-cleaner/
├── main.py                 # 应用入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖包
├── ui/                    # UI界面
│   └── main_window.py    # 主窗口
└── core/                  # 核心逻辑
    ├── file_scanner.py   # 文件扫描
    ├── ai_analyzer.py    # AI分析（需要配置）
    └── file_manager.py   # 文件操作
```

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置通义千问API

**重要：必须配置API才能使用AI功能！**

在 `config.py` 中填写你的通义千问 API Key：

```python
# 通义千问 API 配置
TONGYI_API_KEY = "sk-ac83350d4bc3493ab2a0dcc754b8c44e"  # 在这里填写
TONGYI_MODEL = "qwen3-coder-plus"  # 可选: qwen-max, qwen-plus, qwen-turbo
```

### 3. 实现AI接口

打开 `core/ai_analyzer.py`，找到 `_call_tongyi_api` 方法（约第108行），按照注释实现通义大模型调用。

#### 方法1: 使用 dashscope SDK（推荐）

```python
def _call_tongyi_api(self, prompt: str) -> str:
    import dashscope
    from dashscope import Generation

    dashscope.api_key = self.api_key

    response = Generation.call(
        model=self.model,
        prompt=prompt,
        result_format='message'
    )

    if response.status_code == 200:
        return response.output.text
    else:
        raise Exception(f"API调用失败: {response.message}")
```

#### 方法2: 使用 HTTP 请求（OpenAI兼容模式）

```python
def _call_tongyi_api(self, prompt: str) -> str:
    import requests

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": self.model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data, timeout=config.AI_TIMEOUT)
    result = response.json()
    return result['choices'][0]['message']['content']
```

## 使用方法

### 1. 运行程序

```bash
python main.py
```

### 2. 扫描文件

点击"开始扫描"按钮，程序会自动扫描桌面和下载文件夹。

### 3. AI分析

扫描完成后，点击"AI分析"按钮，通义千问会分析文件并给出整理建议。

### 4. 执行操作

查看AI建议后，点击"执行操作"按钮确认执行。

**注意：执行前会自动备份文件到 `桌面/备份文件夹`！**

## 配置说明

在 `config.py` 中可以自定义以下配置：

### 扫描路径

```python
DEFAULT_SCAN_PATHS = [
    str(Path.home() / "Desktop"),   # 桌面
    str(Path.home() / "Downloads"), # 下载文件夹
]
```

### 忽略规则

```python
# 忽略的文件扩展名
IGNORE_EXTENSIONS = ['.ini', '.sys', '.dll']

# 忽略的文件夹
IGNORE_FOLDERS = ['$RECYCLE.BIN', 'System Volume Information']
```

### 备份设置

```python
BACKUP_FOLDER = str(Path.home() / "Desktop" / "备份文件夹")
ENABLE_BACKUP = True  # 是否在删除前备份
```

## 获取通义千问API Key

1. 访问 [阿里云百炼平台](https://www.aliyun.com/product/bailian)
2. 注册/登录账号
3. 开通通义千问服务
4. 创建 API Key
5. 将 API Key 填入 `config.py`

## 注意事项

1. **备份功能**：建议保持 `ENABLE_BACKUP = True`，防止误删重要文件
2. **API费用**：通义千问API按调用量收费，请关注使用量
3. **文件安全**：执行删除操作前请仔细检查AI建议
4. **权限问题**：某些系统文件可能无法访问，属正常现象

## 常见问题

### Q: AI分析失败怎么办？

A: 检查以下几点：
- API Key是否正确填写
- 网络连接是否正常
- `ai_analyzer.py` 中的 `_call_tongyi_api` 方法是否正确实现

### Q: 扫描不到文件？

A: 检查：
- 扫描路径是否正确
- 是否有文件被忽略规则过滤

### Q: 执行操作时出错？

A: 可能原因：
- 文件被其他程序占用
- 没有文件访问权限
- 磁盘空间不足

## 开发说明

### 核心模块

#### file_scanner.py
- `FileScanner`: 文件扫描器
- `FileInfo`: 文件信息类
- 支持递归扫描、进度回调

#### ai_analyzer.py
- `AIAnalyzer`: AI分析器
- **需要实现 `_call_tongyi_api` 方法**
- 负责构造提示词、解析响应

#### file_manager.py
- `FileManager`: 文件管理器
- 支持删除、移动、备份操作

#### main_window.py
- `MainWindow`: 主界面
- 使用多线程避免界面卡顿
- 实时显示进度

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
