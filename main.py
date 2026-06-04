# ============================================================
# PyInstaller + multiprocessing 修复
# 防止子进程重启 app
# ============================================================
import sys
import os

# 必须在所有其他 import 之前调用 freeze_support
if getattr(sys, 'frozen', False):
    import multiprocessing
    multiprocessing.freeze_support()
    print("[INIT] ✅ multiprocessing.freeze_support() called")

# ============================================================
# macOS App Bundle 工作目录自动切换
# ============================================================
def setup_working_directory():
    """自动切换工作目录到 App Bundle 的 Contents/MacOS 目录"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后的环境
        executable_path = sys.executable
        app_bundle_dir = os.path.dirname(executable_path)

        # 如果在 .app bundle 内，切换到 Contents/MacOS
        if app_bundle_dir.endswith('.app/Contents/MacOS'):
            os.chdir(app_bundle_dir)
            print(f"[INIT] ✅ Working directory set to: {app_bundle_dir}")
        else:
            print(f"[INIT] Running from: {app_bundle_dir}")
    else:
        # 开发环境
        print(f"[INIT] Development mode, cwd: {os.getcwd()}")

# 在导入其他模块之前先设置工作目录
setup_working_directory()

# ============================================================
# 设置 multiprocessing 启动方法（必须在 import multiprocessing 之后）
# ============================================================
try:
    # 注意：freeze_support 后不能再调用 set_start_method
    # 所以在 frozen 环境下跳过这一步
    if not getattr(sys, 'frozen', False):
        import multiprocessing
        if sys.platform == 'darwin':
            multiprocessing.set_start_method('fork', force=True)
            print("[INIT] ✅ Multiprocessing start method set to 'fork'")
except Exception as e:
    print(f"[INIT] ⚠️  Could not set multiprocessing start method: {e}")

# ============================================================
# 导入其他模块
# ============================================================
import qdarktheme
import cv2
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox, QProgressBar, QFileDialog, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal
from ui.timeline import Timeline
from ui.info import Info
from ui.analyze import Analyze
from ui.subtitle import Subtitle
from concurrent.futures import ThreadPoolExecutor
from ui.vlcPlayer import VLCPlayer
from ui.control import Control
from algorithms.model_path import get_model_path, set_model_path, get_missing_models, DEFAULT_MODEL_DIR


class ModelSettingsDialog(QDialog):
    """模型路径设置对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Path Settings")
        self.setMinimumWidth(600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # TransNetV2 模型路径
        transnet_group = QGroupBox("TransNetV2 Model (Shot Detection)")
        transnet_layout = QFormLayout()
        self.transnet_path_edit = QLineEdit()
        self.transnet_path_edit.setReadOnly(True)
        self.transnet_path_edit.setText(get_model_path("transnetv2") or "Not configured")
        
        transnet_btn = QPushButton("Browse...")
        transnet_btn.clicked.connect(lambda: self.browse_model("transnetv2"))
        
        transnet_layout.addRow("Path:", self.transnet_path_edit)
        transnet_layout.addRow("", transnet_btn)
        transnet_group.setLayout(transnet_layout)
        
        # Whisper 模型路径
        whisper_group = QGroupBox("Whisper Model (Subtitle Recognition)")
        whisper_layout = QFormLayout()
        self.whisper_path_edit = QLineEdit()
        self.whisper_path_edit.setReadOnly(True)
        self.whisper_path_edit.setText(get_model_path("whisper") or "Not configured")

        whisper_btn = QPushButton("Browse...")
        whisper_btn.clicked.connect(lambda: self.browse_model("whisper"))

        whisper_layout.addRow("Path:", self.whisper_path_edit)
        whisper_layout.addRow("", whisper_btn)
        whisper_group.setLayout(whisper_layout)

        # OpenPose 模型路径
        openpose_group = QGroupBox("OpenPose Model (Shot Scale Analysis)")
        openpose_layout = QFormLayout()
        self.openpose_path_edit = QLineEdit()
        self.openpose_path_edit.setReadOnly(True)
        self.openpose_path_edit.setText(get_model_path("openpose") or "Not configured")

        openpose_btn = QPushButton("Browse...")
        openpose_btn.clicked.connect(lambda: self.browse_model("openpose"))

        openpose_layout.addRow("Path:", self.openpose_path_edit)
        openpose_layout.addRow("", openpose_btn)
        openpose_group.setLayout(openpose_layout)
        
        # 默认路径提示
        info_label = QLabel(f"<i>Default model directory:<br>{DEFAULT_MODEL_DIR}</i>")
        info_label.setWordWrap(True)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_paths)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(ok_btn)
        
        # 添加到主布局
        layout.addWidget(transnet_group)
        layout.addWidget(whisper_group)
        layout.addWidget(openpose_group)
        layout.addWidget(info_label)
        layout.addLayout(btn_layout)
    
    def browse_model(self, model_name):
        """浏览选择模型目录"""
        path = QFileDialog.getExistingDirectory(
            self,
            f"Select {model_name.upper()} Model Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        if path:
            # 验证目录是否包含模型文件
            if self.validate_model_dir(path, model_name):
                set_model_path(model_name, path)
                if model_name == "transnetv2":
                    self.transnet_path_edit.setText(path)
                elif model_name == "whisper":
                    self.whisper_path_edit.setText(path)
                else:  # openpose
                    self.openpose_path_edit.setText(path)
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Model Directory",
                    f"The selected directory does not appear to contain {model_name} model files.\n\n"
                    f"Please select the correct model directory."
                )
    
    def validate_model_dir(self, path, model_name):
        """验证目录是否包含模型文件"""
        if model_name == "transnetv2":
            # TransNetV2 模型应该包含 saved_model.pb 文件
            return os.path.exists(os.path.join(path, "saved_model.pb"))
        elif model_name == "whisper":
            # Whisper 模型应该包含 config.json 或 .pt 文件
            return (os.path.exists(os.path.join(path, "config.json")) or
                    any(f.endswith('.pt') or f.endswith('.bin') for f in os.listdir(path)))
        elif model_name == "openpose":
            # OpenPose 模型应该包含 body_25 或 coco 子目录
            body25_dir = os.path.join(path, "body_25")
            coco_dir = os.path.join(path, "coco")
            has_body25 = os.path.exists(body25_dir) and os.path.exists(os.path.join(body25_dir, "pose_deploy.prototxt"))
            has_coco = os.path.exists(coco_dir) and os.path.exists(os.path.join(coco_dir, "pose_deploy_linevec.prototxt"))
            # 验证传入的目录本身是否包含 prototxt 文件（用户可能直接选择了 body_25 或 coco 目录）
            has_direct = any(f.endswith('.prototxt') for f in os.listdir(path))
            return has_body25 or has_coco or has_direct
        return True
    
    def reset_paths(self):
        """重置为默认路径"""
        config = {"model_paths": {"transnetv2": None, "whisper": None, "openpose": None}}
        from algorithms.config import save_config
        save_config(config)
        self.transnet_path_edit.setText(get_model_path("transnetv2") or "Not configured")
        self.whisper_path_edit.setText(get_model_path("whisper") or "Not configured")
        self.openpose_path_edit.setText(get_model_path("openpose") or "Not configured")


# from ui.subtitleEasyOcr import getsubtitleEasyOcr,subtitle2Srt

class MainWindow(QMainWindow):
    # 定义信号
    filename_changed = Signal(str)  # 文件名更改信号，传递字符串参数
    shot_finished = Signal()        # 表示视频分析完成的信号
    shot_changed = Signal(str)         # 表示在 timeline 中有添加/删除操作，需要更新 info
    video_play_changed = Signal(int)  # 视频播放状态改变信号，传递整数参数

    def __init__(self):
        super().__init__()
        # 创建线程池，用于处理多线程任务
        self.threadpool = ThreadPoolExecutor()
        self.filename = ''  # 当前文件名
        self.frame_save = ""  # 图片存储路径
        self.image_save = ""
        self.AnalyzeImgPath = ''  # Analyze 窗口中要显示的图像的路径
        self.colorsC = 2
        self.init_ui()  # 初始化界面
        self.frameCnt = 0
        
        # 启动时检查模型
        self.check_models_on_startup()

    def init_ui(self):

        # 信号与槽的连接
        self.filename_changed.connect(self.on_filename_changed)  # 文件名更改信号连接到处理方法
        self.on_filename_changed()  # 初始化时调用一次

        # 初始化窗口界面
        # 设置应用图标
        # self.setWindowIcon(QIcon(resource_path('resources/icon.ico')))

        # 延迟导入 VLC，创建 VLC 播放器实例
        self.player = VLCPlayer(self)
        self.setCentralWidget(self.player)  # 设置 VLC 播放器为主窗口的中心部件
        self.video_play_changed.connect(self.player.on_video_play_changed)  # 点击 timeline 中的图片从图片处开始播放

        # 创建其他功能窗口并添加到停靠区域
        self.info = Info(self)  # 信息窗口
        self.addDockWidget(Qt.LeftDockWidgetArea, self.info)  # 停靠到左侧

        self.subtitle = Subtitle(self, self.filename)  # 字幕窗口
        self.addDockWidget(Qt.LeftDockWidgetArea, self.subtitle)

        self.control = Control(self, self.filename)  # 控制窗口
        self.addDockWidget(Qt.RightDockWidgetArea, self.control)# 停靠到右侧

        self.analyze = Analyze(self, self.filename)  # 分析窗口
        self.addDockWidget(Qt.RightDockWidgetArea, self.analyze)

        self.timeline = Timeline(self)  # 时间轴窗口
        self.addDockWidget(Qt.BottomDockWidgetArea, self.timeline)# 停靠到下侧

        # 创建菜单栏
        menu = self.menuBar()

        # 文件菜单
        file_menu = menu.addMenu('&File')  # 添加文件菜单
        open_action = QAction('&Open', self)
        open_action.triggered.connect(lambda: self.player.open_file())  # 打开视频
        exit_action = QAction('&Exit', self)
        exit_action.triggered.connect(lambda: self.close()) # 关闭软件
        file_menu.addAction(open_action)  # 添加到文件菜单
        file_menu.addSeparator()  # 添加分隔线
        file_menu.addAction(exit_action)

        # 帮助菜单
        help_menu = menu.addMenu('&Help')  # 添加帮助菜单
        manual_action = QAction('&Manual', self)  # 使用说明菜单项
        manual_action.triggered.connect(
            lambda: QMessageBox.about(
                self,
                'PyCinemetrics V2.0',
                ' 1-Open Video Play(VLC)\n'
                ' 2-ShotCut(TransnetV2)\n'
                ' 3-Color Analyze(Kmeans)\n'
                ' 4-Subtitle(Whisper)\n'
                ' 5-Object Detection(GIT-base)\n'
                ' 6-Field of view(OpenPose)\n'
            )
        )
        about_action = QAction('&About', self)  # 关于菜单项
        about_action.triggered.connect(
            lambda: QMessageBox.about(self, 'PyCinemetrics', 'PyCinemetrics V2.0 \nHttp://movie.yingshinet.com')
        )
        help_menu.addAction(manual_action)  # 添加使用说明菜单项
        help_menu.addAction(about_action)  # 添加关于菜单项
        
        # 设置菜单
        settings_menu = menu.addMenu('&Settings')  # 添加设置菜单
        models_action = QAction('&Model Paths', self)  # 模型路径设置菜单项
        models_action.triggered.connect(self.open_model_settings)
        settings_menu.addAction(models_action)  # 添加模型路径设置菜单项

        # 状态栏
        status_bar = self.statusBar()
        self.progressBar = QProgressBar()  # 进度条
        status_bar.showMessage('')  # 显示空信息
        status_bar.addPermanentWidget(self.progressBar)  # 在状态栏添加进度条
        self.progressBar.hide()  # 默认隐藏进度条

        # 设置窗口尺寸和位置
        app = QApplication.instance()
        screen = app.primaryScreen()
        geometry = screen.availableGeometry()  # 获取屏幕可用区域
        self.setGeometry(
            int(geometry.width() * 0.1),   # 距屏幕左边的距离
            int(geometry.height() * 0.1),  # 距屏幕上方的距离
            int(geometry.width() * 0.8),   # 窗口宽度
            int(geometry.height() * 0.8)   # 窗口高度
        )
        self.showMaximized()  # 窗口最大化

        # 调整停靠窗口的尺寸
        # 调整高度
        self.resizeDocks([self.info, self.subtitle], [int(self.height() * 0.3), int(self.height() * 0.2)], Qt.Vertical)
        self.resizeDocks([self.control, self.analyze], [int(self.height() * 0.3), int(self.height() * 0.2)], Qt.Vertical)

        # 调整宽度
        self.resizeDocks([self.info, self.subtitle, self.control, self.analyze], [int(self.width() * 0.3)] * 4, Qt.Horizontal)
        # 下方的 timeline
        self.resizeDocks([self.timeline],
                         [int(self.height() * 0.5)], Qt.Vertical)  # 设置底部时间轴窗口的高度

    def on_filename_changed(self, filename=None):
        # 文件名改变时更新窗口标题
        if filename is None or filename == '':
            self.setWindowTitle('PyCinemetrics')  # 无文件时设置默认标题
        else:
            self.setWindowTitle('PyCinemetrics - %s' % filename)  # 显示当前文件名
            self.filename = filename
            # 使用绝对路径：~/Documents/pyCinemetrics/
            video_name = str(os.path.basename(self.filename)[0:-4])
            base_dir = os.path.expanduser('~/Documents/pyCinemetrics')
            os.makedirs(base_dir, exist_ok=True)
            self.frame_save = os.path.join(base_dir, video_name, "frame")  # 图片存储路径
            self.image_save = os.path.join(base_dir, video_name)
            # 确保目录存在
            os.makedirs(self.frame_save, exist_ok=True)
            os.makedirs(self.image_save, exist_ok=True)
            cap = cv2.VideoCapture(self.filename)
            self.frameCnt = cap.get(cv2.CAP_PROP_FRAME_COUNT)

    def check_models_on_startup(self):
        """启动时检查模型，如果缺失则提示用户"""
        missing_models = get_missing_models()
        if missing_models:
            model_names = {
                "transnetv2": "TransNetV2 (Shot Detection)",
                "whisper": "Whisper (Subtitle Recognition)",
                "openpose": "OpenPose (Shot Scale Analysis)"
            }
            missing_names = [model_names.get(m, m) for m in missing_models]

            newline = "\n"
            msg = (f"The following model(s) are missing:\n\n"
                   f"{newline.join(missing_names)}\n\n"
                   f"Models should be placed in:\n{DEFAULT_MODEL_DIR}\n\n"
                   f"You can configure the model path in Settings > Model Paths.\n\n"
                   f"Continue anyway?")

            reply = QMessageBox.warning(
                self,
                'Missing Models',
                msg,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:
                self.open_model_settings()

    def open_model_settings(self):
        """打开模型路径设置对话框"""
        dialog = ModelSettingsDialog(self)
        dialog.exec()


def main():
    # 启用 Qt 高分辨率显示支持
    qdarktheme.enable_hi_dpi()
    # 创建 Qt 应用程序实例
    app = QApplication(sys.argv)
    # 设置 QDarkTheme 主题（深色或浅色主题）
    qdarktheme.setup_theme()

    # 创建主窗口实例
    _ = MainWindow()

    # 启动应用程序事件循环
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
