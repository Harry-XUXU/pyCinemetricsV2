# PyCinemetricsV2 macOS 打包指南

## 📦 快速开始

### 方法一：使用自动化脚本（推荐）

```bash
# 1. 给脚本添加执行权限
chmod +x build_macos.sh

# 2. 运行打包脚本
./build_macos.sh
```

### 方法二：手动打包

```bash
# 1. 确保已安装 PyInstaller
pip install pyinstaller

# 2. 清理旧的构建文件
rm -rf build dist __pycache__

# 3. 使用 spec 文件打包
pyinstaller main_mac.spec --clean

# 4. 测试应用
open dist/pyCinemetricsV2.app
```

## 📋 打包前准备

### 1. 创建专用虚拟环境（推荐）

```bash
# 如果已有 venv 可以跳过
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 PyInstaller
pip install pyinstaller
```

### 2. 设置环境变量

程序运行时需要设置以下环境变量以防止多线程冲突：

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

**注意**: 这些环境变量已配置在 `Info.plist` 中，打包后的 App 会自动设置。

### 3. 检查 ffmpeg（可选）

如果需要使用 ffmpeg 功能：

```bash
# 检查是否已安装
ffmpeg -version

# 如果未安装，使用 Homebrew 安装
brew install ffmpeg
```

## 🔧 配置文件说明

### main_mac.spec 关键配置

- **binaries**: 需要一起打包的可执行文件（如 ffmpeg）
- **datas**: 需要一起打包的数据文件夹
- **hiddenimports**: 隐式导入的模块
- **console**: 
  - `False` = GUI 应用（无终端窗口）
  - `True` = 显示调试信息

## 📱 打包后操作

### 1. 测试应用

```bash
# 直接打开应用
open dist/pyCinemetricsV2.app

# 或者在 Finder 中双击 dist/pyCinemetricsV2.app
```

### 2. 解决"无法打开"的问题

macOS 可能会阻止未签名的应用：

**方法一：系统设置**
```
系统设置 → 隐私与安全性 → 安全性
点击"仍要打开"
```

**方法二：命令行移除隔离属性**
```bash
xattr -cr dist/pyCinemetricsV2.app
```

**方法三：代码签名（需要开发者证书）**
```bash
codesign --force --deep --sign - dist/pyCinemetricsV2.app
```

### 3. 创建 DMG 安装包

```bash
hdiutil create -volname "pyCinemetricsV2" \
               -srcfolder "dist/pyCinemetricsV2.app" \
               -ov -format UDZO "dist/pyCinemetricsV2.dmg"
```

## ⚠️ 常见问题解决

### 问题 1: 应用启动后立即退出

**原因**: 缺少某些依赖或资源文件

**解决方法**:
1. 在终端运行应用查看错误信息：
   ```bash
   ./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2
   ```
2. 根据错误信息调整 `main_mac.spec` 中的 `datas` 和 `hiddenimports`

### 问题 2: 缺少某些 Python 模块

**解决方法**:
在 `main_mac.spec` 的 `hiddenimports` 中添加缺失的模块名

### 问题 3: 找不到模型文件或字体

**解决方法**:
确保 `main_mac.spec` 的 `datas` 中包含这些文件夹：
```python
datas=[
    ('algorithms', 'algorithms'),
    ('ui', 'ui'),
    ('models', 'models'),
    ('fonts', 'fonts'),
    ('resources', 'resources'),
],
```

### 问题 4: 应用体积过大

**优化方法**:
1. 使用专用虚拟环境（只包含必要的包）
2. 排除不必要的模块：
   ```python
   excludes=['tkinter', 'pytest', 'nose'],
   ```
3. 启用 UPX 压缩（已在配置中启用）

## 🎯 高级配置

### 针对 Apple Silicon (M1/M2) 优化

```python
# 在 main_mac.spec 中设置
target_arch='arm64'  # 或 'universal2' 支持通用二进制
```

### 添加应用图标

```python
# 在 EXE 部分添加 icon 参数（需要 .icns 格式）
icon='resources/icon.icns',
```

转换图标格式：
```bash
# 将 PNG 转换为 ICNS
mkdir icon.iconset
sips -z 512 512 resources/icon.png --out icon.iconset/icon_512x512.png
sips -z 256 256 resources/icon.png --out icon.iconset/icon_256x256.png
sips -z 128 128 resources/icon.png --out icon.iconset/icon_128x128.png
iconutil -c icns icon.iconset -o resources/icon.icns
```

## 📊 打包输出结构

```
dist/
├── pyCinemetricsV2.app/          # macOS 应用程序
│   ├── Contents/
│   │   ├── Info.plist
│   │   ├── MacOS/
│   │   │   └── pyCinemetricsV2   # 可执行文件
│   │   └── Resources/            # 所有资源文件
│   └── PkgInfo
└── pyCinemetricsV2.dmg           # 安装包（可选）
```

## 💡 最佳实践

1. **始终在干净的虚拟环境中打包**
   - 避免引入不必要的依赖
   - 减少最终文件大小

2. **测试后再分发**
   - 在另一台 Mac 上测试
   - 确保没有硬编码的路径

3. **版本管理**
   - 为不同版本创建不同的构建
   - 保留旧的 spec 文件作为参考

4. **文档更新**
   - 记录每次打包的配置变更
   - 维护已知问题列表

## 🆘 获取帮助

如果遇到其他问题：
1. 查看详细构建日志：`build/pyCinemetricsV2/warn-pyCinemetricsV2.txt`
2. 搜索 PyInstaller 官方文档
3. 检查项目 GitHub Issues
