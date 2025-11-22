#!/bin/bash
# -*- coding: utf-8 -*-
# Desktop Cleaner 打包脚本 (Linux/macOS)
# 使用此脚本将应用打包成独立可执行文件

# 设置 UTF-8 编码以正确显示中文
# 优先使用中文 locale，如果不存在则使用英文 UTF-8
if locale -a 2>/dev/null | grep -q "zh_CN.UTF-8\|zh_CN.utf8"; then
    export LANG=zh_CN.UTF-8
    export LC_ALL=zh_CN.UTF-8
elif locale -a 2>/dev/null | grep -q "en_US.UTF-8\|en_US.utf8"; then
    export LANG=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
else
    export LANG=C.UTF-8
    export LC_ALL=C.UTF-8
fi

echo "========================================"
echo "Desktop Cleaner 打包工具"
echo "========================================"
echo ""

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.8-3.11"
    exit 1
fi

# 检查 Python 版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "检测到 Python 版本: $PYTHON_VERSION"

# 提取主版本号和次版本号
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

# 检查版本是否在支持范围内 (3.8-3.11)
if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 8 ]); then
    echo "[错误] Python 版本过低，需要 Python 3.8-3.11"
    echo "当前版本: $PYTHON_VERSION"
    exit 1
fi

if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -gt 11 ]; then
    echo "[警告] Python 版本过高，PyInstaller 可能不兼容"
    echo "当前版本: $PYTHON_VERSION"
    echo "推荐版本: Python 3.8-3.11"
    echo ""
    read -p "是否继续？此操作可能失败... (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "[1/4] 检查并安装依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

echo ""
echo "[2/4] 清理旧的构建文件..."
rm -rf .build_temp dist

echo ""
echo "[3/4] 开始打包应用..."
echo "这可能需要几分钟时间，请耐心等待..."
pyinstaller build/desktop_cleaner.spec

echo ""
echo "[4/4] 检查打包结果..."
if [ -f "dist/DesktopCleaner" ]; then
    echo ""
    echo "========================================"
    echo "打包成功！"
    echo "========================================"
    echo ""
    echo "可执行文件位置: dist/DesktopCleaner"
    echo ""
    echo "你可以："
    echo "1. 直接运行 ./dist/DesktopCleaner"
    echo "2. 将 dist/DesktopCleaner 复制到任何位置使用"
    echo "3. 分享给其他用户（无需安装 Python）"
    echo ""

    # 添加执行权限
    chmod +x dist/DesktopCleaner
    echo "已自动添加执行权限"
    echo ""
else
    echo ""
    echo "========================================"
    echo "打包失败！"
    echo "========================================"
    echo "请查看上方的错误信息"
    echo ""
    exit 1
fi
