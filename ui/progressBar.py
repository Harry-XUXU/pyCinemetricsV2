from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, QRect, QThread, Signal
from PySide6.QtGui import QCloseEvent

# 全局列表，保持所有进度条引用，防止被垃圾回收
_active_progress_bars = []

# 导出 QThread 和 Signal，供其他模块使用
__all__ = ['pyqtbar', 'QThread', 'Signal', 'cleanup_progress_bars']

class ProcessBar(QtWidgets.QDialog):
    def __init__(self, work):
        super().__init__()
        self.work = work
        self.pbar = None
        self.run_work()

    def call_backlog(self, msg, task_number, total_task_number, task_name="Model loading..."):
        if task_number == 0 and total_task_number == 0:
            self.setWindowTitle(self.tr(task_name))
        elif msg == 101 and task_number == 101 and total_task_number == 101:
            print("Thread quit")
            # 只关闭当前窗口，不清理所有进度条
            self._cleanup_self()
            self.close()
        else:
            # 显示任务名称和进度
            label = f"Processing: {task_name} (Task {task_number}/{total_task_number})"
            self.setWindowTitle(self.tr(label))  # 更新窗口标题

        # 更新进度条的值
        if self.pbar:
            self.pbar.setValue(int(msg))
    
    def _cleanup_self(self):
        """清理当前进度条的全局引用"""
        global _active_progress_bars
        # 从全局列表中移除当前进度条
        _active_progress_bars = [bar for bar in _active_progress_bars if bar.myshow != self]
        print(f"[ProgressBar] Cleaned up, {len(_active_progress_bars)} bars remaining")

    def run_work(self):
        # 设置窗口属性
        self.setWindowTitle("Processing...")
        self.setModal(False)  # 非模态，允许与其他窗口交互
        self.setMinimumWidth(500)
        self.setMinimumHeight(100)

        # 不设置 WindowStaysOnTopHint，让窗口正常显示
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # 创建布局
        layout = QtWidgets.QVBoxLayout(self)

        # 进度条设置
        self.pbar = QtWidgets.QProgressBar(self)
        self.pbar.setMinimum(0)
        self.pbar.setMaximum(100)
        self.pbar.setValue(0)

        # 添加进度条到布局
        layout.addWidget(self.pbar)

        # 显示窗口 - 强制居中显示
        self.show()
        self.raise_()  # 将窗口提升到最前面
        self.activateWindow()  # 激活窗口

        # 将窗口移动到屏幕中央
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

        # 创建线程并连接信号（在窗口显示后启动线程）
        self.work.signal.connect(self.call_backlog)  # 进程连接到 GUI 的事件
        self.work.start()

        print(f"[ProgressBar] ✅ Window shown for task: {self.work}")
        print(f"[ProgressBar] Window geometry: {self.geometry()}")
        print(f"[ProgressBar] Window isVisible: {self.isVisible()}")
        print(f"[ProgressBar] Window pos: {self.pos()}")

    def closeEvent(self, event: QCloseEvent):
        # 停止线程
        try:
            if hasattr(self.work, 'stop'):
                self.work.stop()
        except Exception as e:
            print(f"[ProgressBar] Error stopping work: {e}")
        event.accept()

class pyqtbar():
    def __init__(self, work):
        # 检查是否已有相同任务的进度条在运行
        for existing_bar in _active_progress_bars:
            if existing_bar.myshow.work == work:
                print("[ProgressBar] ⚠️  Progress bar already exists for this task!")
                return
        
        self.myshow = ProcessBar(work)
        work.signal.connect(lambda msg, task_number, total_task_number, task_name:
                            self.myshow.call_backlog(msg, task_number, total_task_number, task_name))
        # 将自身添加到全局列表，防止被垃圾回收
        _active_progress_bars.append(self)
        print(f"[ProgressBar] Created, {len(_active_progress_bars)} active bars")
    
    def cleanup(self):
        """清理进度条"""
        global _active_progress_bars
        if self in _active_progress_bars:
            _active_progress_bars.remove(self)
            print(f"[ProgressBar] Cleaned up, {len(_active_progress_bars)} bars remaining")

def cleanup_progress_bars():
    """清理所有进度条"""
    global _active_progress_bars
    for bar in _active_progress_bars[:]:
        try:
            if hasattr(bar, 'myshow') and hasattr(bar.myshow, 'close'):
                bar.myshow.close()
        except Exception as e:
            print(f"[ProgressBar] Error cleaning up bar: {e}")
    _active_progress_bars.clear()
    print("[ProgressBar] All bars cleaned up")

