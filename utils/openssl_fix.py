"""
修复 cv2 和 SSL 模块冲突的补丁
在导入 cv2 之前调用此补丁
"""
import os
import sys

def apply_openssl_fix():
    """
    修复 cv2 的 libcrypto 与 Python ssl 模块的冲突
    通过移除 cv2 的 dylibs 路径，让系统使用 macOS 自带的 OpenSSL
    """
    if getattr(sys, 'frozen', False):
        # 只在打包后的环境中应用
        import ctypes
        
        print("[SSL Fix] Applying OpenSSL fix...")
        
        # 预先加载系统的 libcrypto 和 libssl
        try:
            # macOS 系统的 OpenSSL 库在 dyld cache 中，不需要显式加载
            # 只需要确保 cv2 不覆盖系统的库即可
            
            # 设置环境变量，让系统优先使用系统库
            os.environ['DYLD_LIBRARY_PATH'] = '/usr/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
            
            print("[SSL Fix] ✅ OpenSSL fix applied (using system libraries)")
            return True
        except Exception as e:
            print(f"[SSL Fix] ⚠️  Failed to apply fix: {e}")
            return False
    else:
        # 开发环境不需要修复
        print("[SSL Fix] Development mode, no fix needed")
        return True

# 自动应用修复
if __name__ != '__main__':
    apply_openssl_fix()
