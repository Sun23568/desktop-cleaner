# -*- mode: python ; coding: utf-8 -*-
"""
Desktop Cleaner PyInstaller 配置文件
使用此文件可以自定义打包选项
"""

import os
import sys

# 获取项目根目录
# SPECPATH 是 spec 文件所在的目录（build/），向上一级就是项目根目录
spec_root = os.path.dirname(SPECPATH)

block_cipher = None

a = Analysis(
    [os.path.join(spec_root, 'main.py')],
    pathex=[spec_root],
    binaries=[],
    datas=[
        # 如果有资源文件，在这里添加
        # ('resources', 'resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'dashscope',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'scipy',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DesktopCleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为 False 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加 icon='icon.ico' 设置应用图标
)
