#!/bin/bash

# PyCinemetricsV2 macOS 完整打包脚本
# 使用 collect_all 自动收集所有依赖

set -e

echo "======================================"
echo "PyCinemetricsV2 macOS 打包工具"
echo "======================================"
echo ""

cd /Users/harry/pyCinemetricsV2

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

echo "Python: $PYTHON_PATH ($PYTHON_VERSION)"
echo ""

# 验证关键模块
echo "🔍 验证关键模块..."
python -c "import qdarktheme; import darkdetect; import PySide6; print('✅ 所有关键模块已安装')" || {
    echo "❌ 关键模块缺失！请运行：pip install -r requirements.txt"
    exit 1
}
echo ""

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build dist *.spec
echo ""

# 开始打包
echo "📦 开始打包..."
echo ""

./venv/bin/python -m PyInstaller pyCinemetricsV2.spec

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
