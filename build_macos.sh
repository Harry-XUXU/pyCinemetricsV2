#!/bin/bash

# PyCinemetricsV2 macOS 打包脚本
# 使用方法：./build_macos.sh

echo "======================================"
echo "PyCinemetricsV2 macOS 打包工具"
echo "======================================"
echo ""

# 检查是否安装了 PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "错误：未找到 PyInstaller，正在安装..."
    pip install pyinstaller
fi

# 检查是否安装了所有依赖
echo "检查依赖..."
if [ ! -f "requirements.txt" ]; then
    echo "警告：未找到 requirements.txt"
else
    echo "建议：确保已安装所有依赖："
    echo "  pip install -r requirements.txt"
    echo ""
fi

# 清理旧的构建文件
echo "清理旧的构建文件..."
rm -rf build dist __pycache__
echo ""

# 开始打包
echo "开始打包..."
echo "使用配置文件：main_mac.spec"
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
    echo "分发应用："
    echo "  可以将 dist/pyCinemetricsV2.app 复制到 Applications 文件夹"
    echo "  或者创建 DMG 安装包"
    echo ""
    
    # 可选：创建 DMG
    read -p "是否创建 DMG 安装包？(y/n): " create_dmg
    if [ "$create_dmg" = "y" ]; then
        echo "创建 DMG 文件..."
        hdiutil create -volname "pyCinemetricsV2" \
                       -srcfolder "dist/pyCinemetricsV2.app" \
                       -ov -format UDZO "dist/pyCinemetricsV2.dmg"
        echo "DMG 文件已创建：dist/pyCinemetricsV2.dmg"
    fi
else
    echo ""
    echo "======================================"
    echo "❌ 打包失败！"
    echo "======================================"
    echo "请检查错误日志并尝试以下操作："
    echo "1. 确保所有 Python 依赖已安装"
    echo "2. 检查 main_mac.spec 配置是否正确"
    echo "3. 查看详细错误信息在 build/ 目录中"
    echo ""
fi
