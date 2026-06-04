# PyCinemetricsV2 macOS 打包说明

## 📦 快速开始

### 方式一：使用启动脚本（开发环境）

```bash
# 直接运行启动脚本
./run.sh
```

这会自动：
- ✅ 激活虚拟环境
- ✅ 设置环境变量
- ✅ 启动程序

### 方式二：手动启动（开发环境）

```bash
cd ~/pyCinemetricsV2
source venv/bin/activate
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python3 main.py
```

### 方式三：打包成 App（生产环境）

```bash
# 运行打包脚本
./build_macos.sh
```

打包完成后会在 `dist/` 目录生成 `pyCinemetricsV2.app`

## 🎯 环境变量配置

程序运行时需要设置以下环境变量以防止多线程冲突：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `OPENBLAS_NUM_THREADS` | `1` | OpenBLAS 线程数 |
| `OMP_NUM_THREADS` | `1` | OpenMP 线程数 |
| `MKL_NUM_THREADS` | `1` | MKL 线程数 |
| `VECLIB_MAXIMUM_THREADS` | `1` | Accelerate 框架线程数 |
| `NUMEXPR_NUM_THREADS` | `1` | NumExpr 线程数 |

**重要**: 
- 开发环境：需要手动设置（`run.sh` 已自动配置）
- 生产环境：已集成到 `Info.plist`，App 会自动设置

## 📁 项目结构

```
pyCinemetricsV2/
├── run.sh                  # 开发环境启动脚本
├── build_macos.sh          # 打包脚本
├── launcher.sh             # App 内部启动脚本
├── Info.plist              # macOS 应用配置（包含环境变量）
├── main_mac.spec           # PyInstaller 配置文件
├── MACOS_BUILD_GUIDE.md    # 详细打包指南
├── venv/                   # Python 虚拟环境
└── ...
```

## 🔧 常见问题

### Q1: 为什么要设置环境变量？

**A**: PyCinemetricsV2 使用了多个科学计算库（NumPy、OpenBLAS、MKL 等），这些库默认会使用多线程。在 macOS 上可能导致：
- 性能下降
- 程序崩溃
- 界面卡顿

设置为 1 可以确保单线程运行，避免问题。

### Q2: 打包后的 App 双击无法打开？

**A**: macOS 安全机制阻止未签名应用，解决方法：

**方法 1**: 系统设置
```
系统设置 → 隐私与安全性 → 安全性 → "仍要打开"
```

**方法 2**: 命令行
```bash
xattr -cr dist/pyCinemetricsV2.app
```

### Q3: 提示找不到模块？

**A**: 确保在虚拟环境中打包：
```bash
source venv/bin/activate
./build_macos.sh
```

### Q4: App 体积过大？

**A**: 优化建议：
1. 使用干净的虚拟环境（仅安装必要依赖）
2. 排除不需要的模块（已在 spec 中配置）
3. 启用 UPX 压缩（已在 spec 中启用）

## 🚀 完整打包流程

### 步骤 1: 准备环境

```bash
# 如果还没有虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt

# 安装打包工具
pip install pyinstaller
```

### 步骤 2: 测试运行

```bash
# 使用 run.sh 测试
./run.sh

# 或者手动运行
source venv/bin/activate
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python3 main.py
```

### 步骤 3: 打包

```bash
# 清理旧文件
rm -rf build dist __pycache__

# 打包
pyinstaller main_mac.spec --clean

# 或使用自动化脚本
./build_macos.sh
```

### 步骤 4: 测试 App

```bash
# 查看生成的文件
ls -lh dist/

# 测试运行
open dist/pyCinemetricsV2.app

# 或在终端运行查看详细日志
./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2
```

### 步骤 5: 创建 DMG（可选）

```bash
hdiutil create -volname "pyCinemetricsV2" \
               -srcfolder "dist/pyCinemetricsV2.app" \
               -ov -format UDZO "dist/pyCinemetricsV2.dmg"
```

## 📊 输出文件

打包成功后会生成：

```
dist/
├── pyCinemetricsV2.app      # macOS 应用程序（约 2-3 GB）
└── pyCinemetricsV2.dmg      # 安装包（可选，约 1-2 GB）
```

## ⚙️ 高级配置

### 自定义 Info.plist

如果需要修改环境变量或其他配置，编辑 `Info.plist`：

```xml
<key>LSEnvironment</key>
<dict>
    <key>OPENBLAS_NUM_THREADS</key>
    <string>1</string>
    <!-- 添加其他变量 -->
</dict>
```

### 针对 Apple Silicon 优化

编辑 `main_mac.spec`：

```python
exe = EXE(
    ...
    target_arch='arm64',  # M1/M2 芯片
    # 或 'universal2' 支持通用二进制
)
```

### 添加应用图标

1. 准备 `.icns` 格式图标
2. 编辑 `main_mac.spec`：

```python
exe = EXE(
    ...
    icon='resources/icon.icns',
)
```

## 🆘 故障排查

### 查看详细错误信息

```bash
# 运行 App 并输出日志
./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2

# 查看构建日志
cat build/pyCinemetricsV2/warn-pyCinemetricsV2.txt
```

### 缺少某些文件

编辑 `main_mac.spec` 的 `datas` 部分：

```python
datas=[
    ('algorithms', 'algorithms'),
    ('ui', 'ui'),
    ('models', 'models'),
    ('fonts', 'fonts'),
    ('resources', 'resources'),
    # 添加缺失的文件
]
```

### 缺少某些模块

编辑 `main_mac.spec` 的 `hiddenimports` 部分：

```python
hiddenimports=[
    'numpy',
    'scipy',
    # 添加缺失的模块
]
```

## 📝 版本信息

- **软件版本**: 2.0
- **最低 macOS**: 10.15 (Catalina)
- **Python 版本**: 3.10+
- **PyInstaller 版本**: 5.0+

## 🌐 相关资源

- [PyInstaller 官方文档](https://pyinstaller.org/)
- [macOS App 分发指南](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
- [详细打包指南](MACOS_BUILD_GUIDE.md)

---

**最后更新**: 2026-03-12
