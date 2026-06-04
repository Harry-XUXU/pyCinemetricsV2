"""
资源路径管理器
解决 PyInstaller 打包后资源文件路径问题
"""
import os
import sys

def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径
    
    Args:
        relative_path: 相对于项目根目录的路径，如 'models/transnetv2-weights'
    
    Returns:
        资源文件的绝对路径
    """
    # 检查是否是打包后的环境
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的环境
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 创建的临时目录
            base_path = sys._MEIPASS
        else:
            # .app bundle 的 Contents/MacOS 目录
            executable_path = sys.executable
            base_path = os.path.dirname(executable_path)
            
            # 如果在 .app bundle 内，资源在 Resources 目录
            if base_path.endswith('.app/Contents/MacOS'):
                # 尝试 Resources 目录
                resources_path = os.path.join(os.path.dirname(base_path), 'Resources')
                if os.path.exists(os.path.join(resources_path, relative_path)):
                    base_path = resources_path
    else:
        # 开发环境，使用项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    full_path = os.path.join(base_path, relative_path)
    
    # 调试输出
    print(f"[Resource] {relative_path} -> {full_path}")
    print(f"[Resource] Exists: {os.path.exists(full_path)}")
    
    return full_path


def get_models_path():
    """获取 models 目录路径"""
    return get_resource_path('models')


def get_fonts_path():
    """获取 fonts 目录路径"""
    return get_resource_path('fonts')


def get_resources_path():
    """获取 resources 目录路径"""
    return get_resource_path('resources')
