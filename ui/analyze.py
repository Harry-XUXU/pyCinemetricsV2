import os
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDockWidget, QLabel, QDialog, QVBoxLayout, QTabWidget, QWidget, QHBoxLayout, QPushButton
)
from PySide6.QtCore import Qt


class Analyze(QDockWidget):
    def __init__(self,parent,filename):
        super().__init__('Analyze', parent)
        self.parent = parent
        self.filename = filename
        self.parent.filename_changed.connect(self.on_filename_changed)
        self.init_analyze()

    def init_analyze(self):
        # 使用 QTabWidget 来支持多个标签页
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # 添加一个"重新加载"按钮
        self.reload_button = QPushButton("🔄 Reload Analysis", self)
        self.reload_button.clicked.connect(self.reload_all_tabs)
        
        # 创建容器 widget 来包含 tab_widget 和 reload_button
        container_widget = QWidget(self)
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.reload_button)
        container_layout.addWidget(self.tab_widget)
        
        self.setWidget(container_widget)  # 将容器设置为 QDockWidget 的中央部件
    
    def reload_all_tabs(self):
        """重新加载所有分析标签页"""
        self.tab_widget.clear()
        self.on_filename_changed()


    def on_filename_changed(self):
        # 清空当前显示的所有标签页
        self.tab_widget.clear()

        # 扩展图片列表，包含所有可能的分析结果
        image_names = [
            "shotlength.png",
            "subtitle_wc.png",
            "intertitle.png",
            "metadata.png",
            "wordcloud_ch.png",
            "wordcloud_en.png",
            "shotscale.png",
            "colors.png",
            "scatter_3d.png",  # Color Analysis 的 3D 图
            "pace.png",
            "pace_reversed.png",
            "translated.png",  # 翻译结果
            "image2Text.png",  # 目标检测结果
        ]
        image_paths = [os.path.join(self.parent.image_save, image_name) for image_name in image_names]
        for idx, img_path in enumerate(image_paths):
            # print(img_path)
            if os.path.exists(img_path):
                self.add_tab_with_image(image_names[idx][0:-4], img_path)
        
        # 扫描目录中所有 PNG 文件
        self.scan_existing_results()
    
    def scan_existing_results(self):
        """扫描目录中所有已有的分析结果"""
        if not os.path.exists(self.parent.image_save):
            return
        
        # 获取所有 PNG 文件
        existing_files = [f for f in os.listdir(self.parent.image_save) if f.endswith('.png')]
        
        # 获取当前已有的标签页名称
        existing_tabs = set()
        for i in range(self.tab_widget.count()):
            tab_name = self.tab_widget.tabText(i)
            existing_tabs.add(tab_name + '.png')
        
        # 添加新的 PNG 文件
        for filename in existing_files:
            if filename not in existing_tabs:
                # 跳过已知的文件
                if filename in ['icon-windowed.icns']:
                    continue
                img_path = os.path.join(self.parent.image_save, filename)
                tab_name = filename[0:-4]  # 去掉 .png 后缀
                self.add_tab_with_image(tab_name, img_path)
                print(f"[Analyze] Added existing result: {tab_name}")

    def add_tab_with_image(self, tab_name, image_path):
        # 创建一个标签页来显示图片
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            return  # 如果图片为空，则返回

        # 创建标签并设置图片
        label = QLabel(self)
        label.setPixmap(pixmap.scaled(300, 250, Qt.KeepAspectRatio))  # 设置缩放后的图片大小
        label.mousePressEvent = lambda event: self.on_analyze_image_click(event, image_path)  # 支持点击图片刷新

        # 创建一个布局并将标签添加到布局中
        layout = QVBoxLayout()

        # 将图片标签添加到垂直布局中
        layout.addWidget(label)

        # 创建一个 QWidget 作为标签页的内容
        tab_widget_content = QWidget(self)
        tab_widget_content.setLayout(layout)

        # 添加标签页到 QTabWidget
        self.tab_widget.addTab(tab_widget_content, tab_name)

        # 自动聚焦到当前新建的标签页
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

    def close_tab(self):
        # 获取当前选中的标签页并移除
        current_index = self.tab_widget.currentIndex()
        if current_index != -1:
            self.tab_widget.removeTab(current_index)

    def on_analyze_image_click(self, event, image_path):
        # print(image_path)
        if event.button() == Qt.LeftButton:
            # 获取原始图片
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 获取原始宽度和高度
                original_width = pixmap.width()
                original_height = pixmap.height()

                # 如果图片的宽度大于1600，按比例缩小
                target_width = 1600
                if original_width > target_width:
                    # 根据目标宽度计算新的高度，保持长宽比
                    target_height = int((original_height * target_width) / original_width)
                    # 缩放图像，保持比例
                    scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.KeepAspectRatio)
                else:
                    # 如果图片的宽度小于或等于1600，保持原尺寸
                    scaled_pixmap = pixmap
                self.show_zoomed_image(scaled_pixmap)
    
    def show_zoomed_image(self, pixmap):
        # 创建一个新的对话框来显示放大后的图片
        zoomed_dialog = QDialog(self)
        layout = QVBoxLayout()
        zoomed_label = QLabel()
        zoomed_label.setPixmap(pixmap)
        layout.addWidget(zoomed_label)
        zoomed_dialog.setLayout(layout)
        zoomed_dialog.setWindowTitle('Zoomed Image')
        zoomed_dialog.exec_()  # 进入对话框的主事件循环
