#!/bin/bash
# SSL 修复脚本 - 删除冲突的 OpenSSL 库
# 在 PyInstaller 打包后运行此脚本

APP_PATH="dist/pyCinemetricsV2.app"

echo "🔧 SSL Fix: Removing conflicting OpenSSL libraries..."

# 查找并删除冲突的库
find "$APP_PATH" -name "libcrypto.3.dylib" -delete
find "$APP_PATH" -name "libssl.3.dylib" -delete

echo "✅ SSL Fix: Conflicting libraries removed"
echo "✅ The app will now use macOS system OpenSSL"

# 重新签名应用
echo "🔐 Re-signing the app..."
codesign --force --deep --sign - "$APP_PATH"
xattr -cr "$APP_PATH"

echo "✅ Done! The app is ready to use."
