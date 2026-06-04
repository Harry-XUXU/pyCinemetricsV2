# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules
import os
import sys

block_cipher = None

datas = []
binaries = []
hiddenimports = []

# 收集 PySide6
qt_datas, qt_binaries, qt_hiddenimports = collect_all('PySide6')
datas += qt_datas
binaries += qt_binaries
hiddenimports += qt_hiddenimports

# 收集 qdarktheme
qdark_datas, qdark_binaries, qdark_hiddenimports = collect_all('qdarktheme')
datas += qdark_datas
binaries += qdark_binaries
hiddenimports += qdark_hiddenimports

# 收集 darkdetect
dark_datas, dark_binaries, dark_hiddenimports = collect_all('darkdetect')
datas += dark_datas
binaries += dark_binaries
hiddenimports += dark_hiddenimports

# 收集 imageio_ffmpeg 及其 ffmpeg 二进制文件
hiddenimports += ['imageio_ffmpeg']
hiddenimports += ['imageio_ffmpeg.binaries']

# 添加 imageio_ffmpeg 的 ffmpeg 二进制文件
try:
    import imageio_ffmpeg
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Found ffmpeg at: {ffmpeg_path}")
    binaries.append((ffmpeg_path, '.'))
except Exception as e:
    print(f"Warning: Could not find ffmpeg: {e}")

# 收集 moviepy 依赖
hiddenimports += ['moviepy']
hiddenimports += ['moviepy.editor']

# 收集 pydub 依赖
hiddenimports += ['pydub']

# 收集 ffmpeg-python 依赖
hiddenimports += ['ffmpeg']

# 收集 faster-whisper 依赖
hiddenimports += ['faster_whisper']
hiddenimports += ['ctranslate2']

# 收集 Cython 数据文件
cython_datas, cython_binaries, cython_hiddenimports = collect_all('Cython')
datas += cython_datas
binaries += cython_binaries
hiddenimports += cython_hiddenimports

# 手动添加 Cython Utility 目录
datas.append(('/Users/harry/pyCinemetricsV2/venv/lib/python3.10/site-packages/Cython/Utility', 'Cython/Utility'))

# 收集 setuptools 数据文件
setuptools_datas, setuptools_binaries, setuptools_hiddenimports = collect_all('setuptools')
datas += setuptools_datas
binaries += setuptools_binaries
hiddenimports += setuptools_hiddenimports

# 收集 ssl 相关依赖
hiddenimports += ['ssl', '_ssl', 'hashlib', 'base64']

# 收集 paddleocr 依赖
hiddenimports += ['paddleocr']
hiddenimports += ['paddle']
hiddenimports += ['paddle.nn']
hiddenimports += ['paddle.fluid']
hiddenimports += ['paddle.base']
hiddenimports += ['paddle.utils']
hiddenimports += ['paddle.utils.cpp_extension']

# 收集 easyocr 依赖
hiddenimports += ['easyocr']

# 项目数据文件
# 注意：不打包 models 目录，模型从用户目录 ~/Documents/pyCinemetrics/models/ 加载
project_datas = []
for folder in ['ui', 'resources', 'fonts', 'algorithms']:
    if os.path.exists(folder):
        project_datas.append((folder, folder))
datas += project_datas

# 添加词云字体文件
if os.path.exists('./fonts/msyh.ttf'):
    datas.append(('./fonts/msyh.ttf', 'fonts'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt6', 'PyQt5'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# 使用 onedir 模式而不是 onefile 模式
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='pyCinemetricsV2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 调试期间使用控制台模式
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file='entitlements.xml',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pyCinemetricsV2',
)

app = BUNDLE(
    coll,
    name='pyCinemetricsV2.app',
    icon=None,
    bundle_identifier='com.xjs.pyCinemetricsV2',
    info_plist={
        'CFBundleName': 'pyCinemetricsV2',
        'CFBundleDisplayName': 'pyCinemetricsV2',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSMinimumSystemVersion': '10.15',
        'LSUIElement': False,
        'LSBackgroundOnly': False,
        'NSHighResolutionCapable': True,
        'NSSupportsAutomaticGraphicsSwitching': True,
        'NSAppleEventsUsageDescription': 'This app needs to control other applications for video analysis.',
    },
    entitlements_file='entitlements.xml',
)
