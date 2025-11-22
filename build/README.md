# 构建目录

本目录包含打包应用所需的所有文件和脚本。

## 📁 目录结构

```
build/
├── README.md              # 本文件
├── desktop_cleaner.spec   # PyInstaller 配置文件
├── build.bat              # Windows 打包脚本
└── build.sh               # Linux/macOS 打包脚本
```

## 🚀 快速开始

### Windows 用户

从项目根目录运行：
```batch
build\build.bat
```

或直接双击 `build.bat`

### Linux/macOS 用户

从项目根目录运行：
```bash
./build/build.sh
```

或者：
```bash
cd build
./build.sh
```

## 📦 打包过程

脚本会自动执行以下步骤：

1. **检查 Python 环境** - 确保 Python 3.8+ 已安装
2. **安装依赖** - 安装 requirements.txt 中的所有依赖
3. **清理旧文件** - 删除之前的构建产物
4. **执行打包** - 使用 PyInstaller 和 spec 配置文件打包
5. **验证结果** - 检查可执行文件是否成功生成

## 📝 配置文件说明

### desktop_cleaner.spec

这是 PyInstaller 的配置文件，包含：

- **入口文件**: `main.py`
- **隐藏导入**: PyQt6, dashscope, requests 等
- **排除模块**: matplotlib, numpy, pandas 等（减小文件大小）
- **打包模式**: 单文件模式（onefile）
- **控制台**: 关闭（GUI应用）

你可以编辑此文件来：
- 添加应用图标（设置 `icon` 参数）
- 包含额外资源文件（修改 `datas` 列表）
- 调整排除的库（修改 `excludes` 列表）

## 🎯 输出位置

打包成功后，可执行文件位于项目根目录的 `dist/` 文件夹：

- **Windows**: `dist/DesktopCleaner.exe`
- **Linux/macOS**: `dist/DesktopCleaner`

## 🔧 自定义打包

### 添加应用图标

1. 准备图标文件：
   - Windows: `.ico` 格式
   - macOS: `.icns` 格式

2. 编辑 `desktop_cleaner.spec`：
   ```python
   icon='path/to/icon.ico'
   ```

### 修改应用名称

编辑 `desktop_cleaner.spec` 中的 `name` 参数：
```python
name='YourAppName'
```

### 包含资源文件

如果需要打包图片、配置文件等资源：

```python
datas=[
    ('resources', 'resources'),  # 包含整个 resources 目录
    ('config.json', '.'),        # 包含单个文件到根目录
],
```

## 🐛 常见问题

### 打包失败

1. 检查 Python 版本是否 >= 3.8
2. 确保所有依赖已正确安装
3. 查看错误日志定位问题

### 文件过大

编辑 `desktop_cleaner.spec`，在 `excludes` 列表中添加不需要的库。

### 运行时错误

1. 使用 `console=True` 查看错误信息
2. 检查 `hiddenimports` 是否包含所有必要的模块
3. 确保资源文件已正确包含在 `datas` 中

## 📚 更多信息

详细的打包指南请参考：[docs/BUILD_GUIDE.md](../docs/BUILD_GUIDE.md)

---

如有问题，请提交 Issue 或查看 PyInstaller 官方文档。
