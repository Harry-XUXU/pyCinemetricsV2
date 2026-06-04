#!/bin/bash

# PyCinemetricsV2 macOS 完整打包脚本
# 确保所有依赖都被正确收集

set -e

echo "======================================"
echo "PyCinemetricsV2 macOS 完整打包工具"
echo "======================================"
echo ""

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误：未找到虚拟环境 venv"
    exit 1
fi

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source venv/bin/activate

# 显示 Python 信息
PYTHON_PATH=$(which python)
PYTHON_VERSION=$(python --version)
PYINSTALLER_PATH=$(which pyinstaller)

echo "Python: $PYTHON_PATH ($PYTHON_VERSION)"
echo "PyInstaller: $PYINSTALLER_PATH"
echo ""

# 验证关键模块
echo "🔍 验证关键模块..."
python -c "import qdarktheme; import darkdetect; import PySide6; print('✅ 所有关键模块已安装')" || {
    echo "❌ 关键模块缺失！请运行：pip install -r requirements.txt"
    exit 1
}
echo ""

# 清理旧的构建文件
echo "🧹 清理旧的构建文件和缓存..."
rm -rf build dist __pycache__
echo ""

# 开始打包
echo "📦 开始打包..."
echo ""

# 直接运行打包（PyInstaller 会自动处理缓存）
pyinstaller packaging/pyCinemetricsV2.spec

# 检查打包结果
echo ""
if [ -d "dist/pyCinemetricsV2.app" ]; then
    echo "======================================"
    echo "✅ 打包成功！"
    echo "======================================"
    echo "应用程序位置：dist/pyCinemetricsV2.app"
    echo ""
    
    # 显示 App 大小
    APP_SIZE=$(du -sh dist/pyCinemetricsV2.app | cut -f1)
    echo "App 大小：$APP_SIZE"
    echo ""
    
    echo "测试运行："
    echo "  open dist/pyCinemetricsV2.app"
    echo ""
    echo "或者查看详细日志："
    echo "  ./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2"
    echo ""
else
    echo "======================================"
    echo "❌ 打包失败！"
    echo "======================================"
    echo "请检查上面的错误信息"
    echo ""
    exit 1
fi
