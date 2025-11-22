# 项目结构说明

本文档描述了 Desktop Cleaner 项目的目录结构和组织方式。

## 📁 目录结构

```
desktop-cleaner/
├── build/                      # 构建相关文件
│   ├── README.md              # 构建说明
│   ├── build.bat              # Windows 打包脚本
│   ├── build.sh               # Linux/macOS 打包脚本
│   └── desktop_cleaner.spec   # PyInstaller 配置文件
│
├── core/                       # 核心业务逻辑
│   ├── __init__.py
│   ├── ai_analyzer.py         # AI 分析器
│   ├── ai_providers/          # AI 提供商实现
│   │   ├── __init__.py
│   │   ├── base_provider.py   # 基类
│   │   ├── provider_factory.py # 工厂模式
│   │   ├── rule_based_provider.py  # 规则引擎
│   │   └── tongyi_provider.py # 通义千问
│   ├── file_manager.py        # 文件管理器
│   ├── file_scanner.py        # 文件扫描器
│   └── user_config.py         # 用户配置管理
│
├── docs/                       # 文档目录
│   ├── AI_PROVIDERS_GUIDE.md  # AI 提供商指南
│   ├── BATCH_PROGRESS_GUIDE.md # 批处理进度指南
│   ├── BUILD_GUIDE.md         # 打包构建指南
│   ├── CHANGELOG.md           # 更新日志
│   ├── CONFIG_GUIDE.md        # 配置指南
│   ├── FIXED.md               # 已修复问题列表
│   ├── QUICK_START.md         # 快速开始
│   ├── README_AI_PROVIDERS.md # AI 提供商说明
│   ├── TONGYI_API_GUIDE.md    # 通义千问 API 指南
│   └── USER_GUIDE.md          # 用户使用指南
│
├── scripts/                    # 开发辅助脚本
│   ├── README.md              # 脚本说明
│   ├── create-feature-branch.sh # 创建功能分支
│   ├── git-commit.sh          # Git 提交脚本
│   └── merge-to-main.sh       # 合并到主分支
│
├── ui/                         # 用户界面
│   ├── __init__.py
│   ├── main_window.py         # 主窗口
│   └── settings_dialog.py     # 设置对话框
│
├── .gitignore                  # Git 忽略文件
├── config.py                   # 应用配置
├── main.py                     # 应用入口
├── PROJECT_STRUCTURE.md        # 本文件
├── README.md                   # 项目说明
└── requirements.txt            # Python 依赖
```

## 📦 目录说明

### `build/` - 构建目录
存放应用打包相关的文件和脚本。

**主要文件**：
- `desktop_cleaner.spec`: PyInstaller 配置文件
- `build.bat` / `build.sh`: 自动化打包脚本

**用途**：将 Python 应用打包成独立可执行文件

### `core/` - 核心逻辑
包含应用的所有业务逻辑代码。

**模块说明**：
- `ai_analyzer.py`: 协调 AI 分析流程
- `ai_providers/`: 不同 AI 提供商的实现
- `file_manager.py`: 文件操作（移动、删除等）
- `file_scanner.py`: 扫描和分析桌面文件
- `user_config.py`: 配置管理（保存/读取用户设置）

### `docs/` - 文档目录
存放所有项目文档和使用指南。

**文档分类**：
- **用户文档**: USER_GUIDE.md, QUICK_START.md
- **开发文档**: BUILD_GUIDE.md, CONFIG_GUIDE.md
- **API 文档**: AI_PROVIDERS_GUIDE.md, TONGYI_API_GUIDE.md
- **项目文档**: CHANGELOG.md, FIXED.md

### `scripts/` - 脚本目录
开发和维护相关的辅助脚本。

**脚本类型**：
- Git 工作流脚本（分支管理、提交、合并）
- 自动化开发任务脚本

### `ui/` - 界面目录
所有用户界面相关代码。

**组件**：
- `main_window.py`: 主应用窗口
- `settings_dialog.py`: 设置对话框（含自定义控件）

## 🔧 配置文件

### 应用配置
- `config.py`: 默认配置和常量
- `~/.desktop-cleaner/user_config.json`: 用户配置（运行时生成）

### 开发配置
- `requirements.txt`: Python 依赖列表
- `.gitignore`: Git 忽略规则
- `build/desktop_cleaner.spec`: 打包配置

## 🚀 工作流

### 开发流程
1. 使用 `scripts/create-feature-branch.sh` 创建功能分支
2. 进行开发和测试
3. 使用 `scripts/git-commit.sh` 提交代码
4. 使用 `scripts/merge-to-main.sh` 合并到主分支

### 打包流程
1. 运行 `build/build.bat` (Windows) 或 `build/build.sh` (Linux/macOS)
2. 在 `dist/` 目录获取可执行文件
3. 分发给用户

## 📝 命名规范

### 文件命名
- Python 文件: `snake_case.py`
- Markdown 文档: `UPPERCASE.md` 或 `Title_Case.md`
- Shell 脚本: `kebab-case.sh`

### 代码规范
- 类名: `PascalCase`
- 函数/方法: `snake_case`
- 常量: `UPPER_SNAKE_CASE`
- 变量: `snake_case`

## 🔍 重要路径

### 开发时
- 入口文件: `main.py`
- 配置文件: `config.py`
- 用户配置: `core/user_config.py`

### 运行时
- 用户配置: `~/.desktop-cleaner/user_config.json`
- 临时图标: `/tmp/` 或 `%TEMP%`

### 打包后
- 可执行文件: `dist/DesktopCleaner.exe` 或 `dist/DesktopCleaner`

## 📚 扩展指南

### 添加新功能
1. 在 `core/` 中实现核心逻辑
2. 在 `ui/` 中添加界面组件
3. 更新 `docs/` 中的相关文档
4. 如需新依赖，更新 `requirements.txt`

### 添加新的 AI 提供商
1. 在 `core/ai_providers/` 创建新的提供商类
2. 继承 `BaseAIProvider`
3. 在 `provider_factory.py` 中注册
4. 更新 `ui/settings_dialog.py` 添加 UI 选项
5. 更新 `docs/AI_PROVIDERS_GUIDE.md`

### 添加文档
1. 用户文档放在 `docs/`
2. 代码文档使用 docstring
3. 构建相关文档放在 `build/README.md`

## 🎯 最佳实践

1. **保持目录整洁**: 各类文件放在对应目录
2. **文档同步更新**: 代码修改时同步更新文档
3. **使用工具脚本**: 利用 `scripts/` 中的脚本提高效率
4. **遵循命名规范**: 保持代码风格一致
5. **模块化设计**: 保持各模块职责清晰

---

此结构旨在提供清晰的项目组织，便于开发、维护和协作。
