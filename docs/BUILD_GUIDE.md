# Desktop Cleaner 打包指南

本指南将帮助你将 Desktop Cleaner 打包成独立可执行文件，用户无需安装 Python 即可使用。

## 📋 前提条件

在开始打包之前，请确保你已经安装：

- **Python 3.8 - 3.11**（推荐 3.10 或 3.11）
- **pip**（Python 包管理工具）

⚠️ **重要提示**：
- PyInstaller 目前**不支持 Python 3.12 及更高版本**
- 推荐使用 Python 3.10 或 3.11 以获得最佳兼容性
- 如果你已安装 Python 3.12+，请降级或安装并行版本

验证安装：
```bash
# Windows
python --version
pip --version

# Linux/macOS
python3 --version
pip3 --version
```

### Python 版本问题解决方案

如果你的 Python 版本过高（3.12+），有以下选择：

**方案一：安装 Python 3.11（推荐）**
1. 从 [Python 官网](https://www.python.org/downloads/) 下载 Python 3.11
2. 安装时选择"Add to PATH"
3. 使用 `py -3.11` 命令指定版本

**方案二：使用虚拟环境**
```bash
# 使用 pyenv (推荐)
pyenv install 3.11.0
pyenv local 3.11.0

# 或使用 conda
conda create -n desktop-cleaner python=3.11
conda activate desktop-cleaner
```

**方案三：并行安装多个 Python 版本**
- Windows：使用 Python Launcher (`py -3.11`)
- Linux/macOS：使用 `python3.11` 命令

## 🚀 快速开始

### Windows 用户

1. 双击运行 `build.bat`
2. 等待打包完成（可能需要几分钟）
3. 在 `dist` 文件夹中找到 `DesktopCleaner.exe`

### Linux/macOS 用户

1. 打开终端，进入项目目录
2. 运行打包脚本：
   ```bash
   ./build.sh
   ```
3. 等待打包完成（可能需要几分钟）
4. 在 `dist` 文件夹中找到 `DesktopCleaner` 可执行文件

## 📦 手动打包步骤

如果自动脚本遇到问题，可以手动执行以下步骤：

### 1. 安装依赖

```bash
# Windows
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# Linux/macOS
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller
```

### 2. 运行 PyInstaller

```bash
# 使用配置文件打包（推荐）
pyinstaller desktop_cleaner.spec

# 或者使用命令行参数打包
pyinstaller --name=DesktopCleaner \
            --windowed \
            --onefile \
            --clean \
            main.py
```

### 3. 查看结果

打包完成后，可执行文件位于 `dist` 目录：
- **Windows**: `dist/DesktopCleaner.exe`
- **Linux/macOS**: `dist/DesktopCleaner`

## 🎨 自定义打包选项

### 添加应用图标

1. 准备一个 `.ico` 文件（Windows）或 `.icns` 文件（macOS）
2. 编辑 `desktop_cleaner.spec` 文件
3. 修改 `icon=None` 为 `icon='path/to/icon.ico'`

### 包含额外资源文件

如果需要包含图片、配置文件等资源：

编辑 `desktop_cleaner.spec` 中的 `datas` 部分：
```python
datas=[
    ('resources', 'resources'),  # 包含 resources 文件夹
    ('config.json', '.'),        # 包含单个文件
],
```

### 减小文件大小

编辑 `desktop_cleaner.spec`，在 `excludes` 中添加不需要的库：
```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'PIL',
    'scipy',
    'tkinter',
    # 添加其他不需要的库
],
```

## 🐛 常见问题

### Q: 打包后的程序很大（>100MB）

A: 这是正常的。PyInstaller 会打包 Python 解释器和所有依赖。可以：
- 使用 UPX 压缩（已在配置中启用）
- 排除不需要的库（编辑 `excludes` 列表）
- 考虑使用 `--onedir` 替代 `--onefile`

### Q: 打包后运行报错 "Failed to execute script"

A: 可能的原因：
1. 缺少隐藏导入：在 `desktop_cleaner.spec` 的 `hiddenimports` 中添加缺失的模块
2. 缺少资源文件：确保所有需要的文件都在 `datas` 中声明
3. 使用 `--debug=all` 参数查看详细错误信息

### Q: 杀毒软件报警

A: PyInstaller 打包的程序可能被误报为病毒，这是正常现象。可以：
- 将程序添加到杀毒软件白名单
- 使用代码签名（需要购买证书）
- 向杀毒软件厂商报告误报

### Q: 想打包成安装程序

A: 可以使用以下工具创建安装程序：
- **Windows**: [Inno Setup](https://jrsoftware.org/isinfo.php) 或 [NSIS](https://nsis.sourceforge.io/)
- **macOS**: [create-dmg](https://github.com/sindresorhus/create-dmg)
- **Linux**: [AppImage](https://appimage.org/) 或 系统包管理器

## 📊 打包配置说明

### desktop_cleaner.spec 文件结构

```python
# Analysis - 分析阶段
- scripts: 入口脚本（main.py）
- datas: 需要包含的数据文件
- hiddenimports: 隐式导入的模块
- excludes: 排除的模块

# PYZ - 压缩 Python 文件

# EXE - 生成可执行文件
- name: 程序名称
- console: False = 不显示控制台（GUI 应用）
- icon: 应用图标
- onefile: True = 单文件打包
```

## 🔧 高级选项

### 打包时显示控制台（调试用）

编辑 `desktop_cleaner.spec`，设置 `console=True`

### 分析打包大小

```bash
pyinstaller --log-level=DEBUG desktop_cleaner.spec
```

### 清理构建缓存

```bash
# Windows
rmdir /s /q build dist
del *.spec

# Linux/macOS
rm -rf build dist *.spec
```

## 📝 分发给用户

打包完成后，用户使用步骤：

1. **Windows 用户**：
   - 直接双击 `DesktopCleaner.exe` 运行
   - 无需安装 Python 或任何依赖

2. **Linux/macOS 用户**：
   - 添加执行权限：`chmod +x DesktopCleaner`
   - 运行：`./DesktopCleaner`

3. **首次运行**：
   - 程序会在用户目录创建配置文件：`~/.desktop-cleaner/user_config.json`
   - 如需使用 AI 功能，需要在设置中配置 API Key

## 🎯 发布清单

准备发布时，建议包含：

- [ ] 可执行文件（`DesktopCleaner.exe` 或 `DesktopCleaner`）
- [ ] README.md（用户使用说明）
- [ ] LICENSE（许可证）
- [ ] 版本信息和更新日志

## 💡 优化建议

1. **版本号管理**：在 spec 文件中添加版本号
2. **错误日志**：添加日志记录功能，方便调试
3. **自动更新**：考虑集成自动更新功能
4. **多语言支持**：如果有国际化需求

## 📚 参考资料

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [PyQt6 打包指南](https://doc.qt.io/qtforpython/)
- [PyInstaller 常见问题](https://pyinstaller.org/en/stable/common-problems-and-solutions.html)

---

如有问题，请查看 PyInstaller 日志文件或提交 Issue。
