"""
pyCinemetricsV2 配置管理模块
配置文件位置：~/.pyCinemetricsV2.json
"""
import os
import json
from pathlib import Path

# 配置文件路径
CONFIG_FILE = os.path.expanduser("~/.pyCinemetricsV2.json")

# 默认模型目录（用户目录下）
DEFAULT_MODEL_DIR = os.path.expanduser("~/Documents/pyCinemetrics/models")

# 默认配置
DEFAULT_CONFIG = {
    "model_paths": {
        "transnetv2": None,  # TransNetV2 模型路径
        "whisper": None,     # Whisper 模型路径
        "openpose": None,    # OpenPose 模型路径
    },
    "last_video_path": None,
    "language": "zh-CN",
}


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 合并默认配置
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in config[key]:
                                config[key][sub_key] = sub_value
                return config
        except Exception as e:
            print(f"[Config] Error loading config: {e}")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """保存配置文件"""
    try:
        # 确保目录存在
        config_dir = os.path.dirname(CONFIG_FILE)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"[Config] Config saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"[Config] Error saving config: {e}")
        return False


def get_model_path(model_name):
    """
    获取模型路径，按优先级查找：
    1. 用户配置路径（~/.pyCinemetricsV2.json）
    2. 用户目录（~/Documents/pyCinemetrics/models/）
    3. 打包目录（app bundle 内的 models/）
    4. 开发目录（项目根目录的 models/）
    
    Args:
        model_name: 模型名称 ('transnetv2' 或 'whisper')
    
    Returns:
        模型路径字符串，如果找不到则返回 None
    """
    import sys
    
    config = load_config()
    
    # 1. 检查用户配置路径
    configured_path = config.get("model_paths", {}).get(model_name)
    if configured_path and os.path.exists(configured_path):
        print(f"[ModelPath] ✅ Using configured path for {model_name}: {configured_path}")
        return configured_path
    
    # 2. 检查用户目录默认路径
    user_model_dir = os.path.join(DEFAULT_MODEL_DIR, get_model_subdir(model_name))
    if os.path.exists(user_model_dir):
        print(f"[ModelPath] ✅ Using user directory for {model_name}: {user_model_dir}")
        return user_model_dir
    
    # 3. 检查打包目录（App Bundle 内）
    if getattr(sys, 'frozen', False):
        executable_dir = os.path.dirname(sys.executable)
        # 如果在 .app bundle 内，资源在 Resources 目录
        if executable_dir.endswith('.app/Contents/MacOS'):
            resources_dir = os.path.join(os.path.dirname(executable_dir), 'Resources')
            bundled_model_dir = os.path.join(resources_dir, 'models', get_model_subdir(model_name))
            if os.path.exists(bundled_model_dir):
                print(f"[ModelPath] ✅ Using bundled path for {model_name}: {bundled_model_dir}")
                return bundled_model_dir
        else:
            # 普通打包目录
            bundled_model_dir = os.path.join(executable_dir, 'models', get_model_subdir(model_name))
            if os.path.exists(bundled_model_dir):
                print(f"[ModelPath] ✅ Using bundled path for {model_name}: {bundled_model_dir}")
                return bundled_model_dir
    
    # 4. 检查开发目录（项目根目录）
    dev_model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  'models', get_model_subdir(model_name))
    if os.path.exists(dev_model_dir):
        print(f"[ModelPath] ✅ Using development path for {model_name}: {dev_model_dir}")
        return dev_model_dir
    
    # 5. 检查当前工作目录（兼容旧版本）
    cwd_model_dir = os.path.join(os.getcwd(), 'models', get_model_subdir(model_name))
    if os.path.exists(cwd_model_dir):
        print(f"[ModelPath] ✅ Using cwd path for {model_name}: {cwd_model_dir}")
        return cwd_model_dir
    
    print(f"[ModelPath] ⚠️  Model not found for {model_name}")
    return None


def get_model_subdir(model_name):
    """获取模型子目录名"""
    model_dirs = {
        "transnetv2": "transnetv2-weights",
        "whisper": "faster-whisper-small",
        "openpose": "pose",  # OpenPose 模型目录
    }
    return model_dirs.get(model_name, model_name)


def set_model_path(model_name, path):
    """
    设置模型路径配置
    
    Args:
        model_name: 模型名称 ('transnetv2' 或 'whisper')
        path: 模型路径
    
    Returns:
        是否保存成功
    """
    config = load_config()
    if "model_paths" not in config:
        config["model_paths"] = {}
    config["model_paths"][model_name] = path
    return save_config(config)


def check_models_exist():
    """
    检查所有必需模型是否存在
    
    Returns:
        dict: {'transnetv2': True/False, 'whisper': True/False, 'openpose': True/False}
    """
    result = {}
    for model_name in ["transnetv2", "whisper", "openpose"]:
        path = get_model_path(model_name)
        result[model_name] = path is not None and os.path.exists(path)
    return result


def get_missing_models():
    """
    获取缺失的模型列表
    
    Returns:
        list: 缺失的模型名称列表
    """
    missing = []
    for model_name, exists in check_models_exist().items():
        if not exists:
            missing.append(model_name)
    return missing
