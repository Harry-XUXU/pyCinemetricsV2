#!/bin/bash
set -e

echo "=== PyCinemetricsV2 打包脚本 ==="
cd /Users/harry/pyCinemetricsV2

# 激活虚拟环境
source venv/bin/activate

# 确认环境
echo "Python: $(which python) ($(python --version))"
echo "qdarktheme: $(pip show pyqtdarktheme 2>/dev/null | grep Version || echo '未找到')"

# 清理
echo "清理旧构建..."
rm -rf build dist *.spec

# 打包（不带--windowed 以便看错误）
echo "开始打包..."
pyinstaller --name=pyCinemetricsV2 \
  --onefile \
  --collect-all qdarktheme \
  --collect-all darkdetect \
  --collect-all PySide6 \
  --exclude-module PyQt6 \
  --add-data "algorithms:algorithms" \
  --add-data "ui:ui" \
  --add-data "models:models" \
  --add-data "fonts:fonts" \
  --add-data "resources:resources" \
  main.py

echo "✅ 打包完成！"
ls -lh dist/
