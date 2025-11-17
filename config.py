"""
配置文件
"""
import os
from pathlib import Path

# 通义千问 API 配置
TONGYI_API_KEY = "sk-ac83350d4bc3493ab2a0dcc754b8c44e"  # 请在这里填写你的通义API Key
TONGYI_MODEL = "qwen3-coder-plus"  # 可选: qwen-max, qwen-plus, qwen-turbo

# 扫描路径配置
DEFAULT_SCAN_PATHS = [
    str(Path.home() / "Desktop"),  # 桌面
    str(Path.home() / "Downloads"),  # 下载文件夹
]

# 文件过滤配置
# 忽略的文件扩展名
IGNORE_EXTENSIONS = [
    '.ini', '.sys', '.dll'  # 系统文件
]

# 忽略的文件夹
IGNORE_FOLDERS = [
    '$RECYCLE.BIN', 'System Volume Information',
    '.git', 'node_modules', '__pycache__'
]

# 文件大小限制（MB）
MIN_FILE_SIZE = 0  # 最小文件大小（MB），0表示不限制
MAX_FILE_SIZE = 10240  # 最大文件大小（MB），用于警告超大文件

# 备份配置
BACKUP_FOLDER = str(Path.home() / "Desktop" / "备份文件夹")
ENABLE_BACKUP = True  # 是否在删除前备份

# AI 分析配置
MAX_FILES_PER_REQUEST = 20  # 每次发送给AI的最大文件数量（减少以避免超时）
AI_TIMEOUT = 120  # AI请求超时时间（秒）增加到120秒

# UI 配置
WINDOW_TITLE = "智能桌面清理工具"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
