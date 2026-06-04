#!/bin/bash

# PyCinemetricsV2 macOS 打包脚本 - 虚拟环境版本
# 确保在虚拟环境中打包，使用正确的依赖

set -e

echo "======================================"
echo "PyCinemetricsV2 macOS 打包工具"
echo "======================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误：未找到虚拟环境 venv"
    echo "请先创建虚拟环境并安装依赖："
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
echo "✅ 激活虚拟环境..."
source venv/bin/activate

# 显示 Python 信息
echo "Python 路径：$(which python)"
echo "Python 版本：$(python --version)"
echo ""

# 检查 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "⚠️  虚拟环境中未安装 PyInstaller，正在安装..."
    pip install pyinstaller
fi

# 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build dist __pycache__
echo ""

# 开始打包
echo "📦 开始打包..."
pyinstaller main_mac.spec --clean

# 检查打包结果
if [ -d "dist/pyCinemetricsV2.app" ]; then
    echo ""
    echo "======================================"
    echo "✅ 打包成功！"
    echo "======================================"
    echo "应用程序位置：dist/pyCinemetricsV2.app"
    echo ""
    echo "测试运行："
    echo "  open dist/pyCinemetricsV2.app"
    echo ""
    echo "或者查看详细日志："
    echo "  ./dist/pyCinemetricsV2.app/Contents/MacOS/pyCinemetricsV2"
    echo ""
else
    echo ""
    echo "======================================"
    echo "❌ 打包失败！"
    echo "======================================"
    echo "请检查上面的错误信息"
    echo ""
    exit 1
fi
