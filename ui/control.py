import functools
import os
import cv2
import shutil
import numpy as np
import pandas as pd
from PySide6.QtGui import QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QDockWidget, QPushButton, QLabel, QFileDialog, QSlider, QMessageBox, QVBoxLayout,
    QWidget, QGridLayout, QLineEdit, QComboBox
)
from PySide6.QtCore import Qt, QRegularExpression
from algorithms.image2Text import ObjectDetection
from algorithms.shotScale import ShotScale
from algorithms.plotShotLength import TransNetPlot, TransNetThread
from algorithms.shotcutTransNetV2 import TransNetV2
from algorithms.subtitleWhisper import SubtitleProcessorWhisper
from algorithms.translateSubtitles import TranslateSrtProcessor
# 延迟导入 CrewProcessor 和 InterTitle，避免 PyInstaller 打包时的 SSL 冲突
# from algorithms.metaData import CrewProcessor
# from algorithms.interTitle import InterTitle
from algorithms.img2Colors import ColorAnalysis
from algorithms.pace import Similarity
from algorithms.faceRecognize import *
from ui.concatFrameWindow import ConcatFrameWindow
from ui.multiCsvViewerDialog import MultiCsvViewerDialog
from ui.progressBar import pyqtbar
from ui.imageDialog import ImageDialog

class Control(QDockWidget):
    def __init__(self, parent, filename):
        super().__init__('Control', parent)
        self.parent = parent
        self.filename = filename
        self.AnalyzeImg = None
        self.AnalyzeImgPath = "" # 好像没有用到
        self.parent.filename_changed.connect(self.on_filename_changed)
        self.subtitleValue = 48    # 每多少帧检查一次字幕
        self.frameConcatValue = 10 # 拼接时每行的帧图个数
        self.facerecognize_window = None
        self.setMaximumHeight(300)  # 设置最大高度为 500 像素
        self.init_ui()


    def init_ui(self):

        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(1)  # 设置行间距为 1 像素
        grid_layout.setHorizontalSpacing(1)  # 设置列间距为 1 像素
        
        # 按钮
        self.shotcut = self.create_function_button("Shot", self.shotcut_transNetV2)
        self.shotlenimgplot = self.create_function_button("Shotlength", self.plot_transnet_shotlength)

        self.frameconcat = self.create_function_button("Mosaic", self.getframeconcat)
        
        self.subtitle = self.create_function_button("Subtitles", self.getsubtitles)
        self.credits = self.create_function_button("MetaData", self.getcredits)
        self.translate_button = self.create_function_button("Translate", self.translate_srt)
        self.intertitle = self.create_function_button("Intertitle", self.getintertitle)

        self.objects = self.create_function_button("image2Text", self.object_detect)

        self.shotscale = self.create_function_button("ShotScale", self.getshotscale)

        self.colors = self.create_function_button("Colors", self.colorAnalyze)

        self.show_csv = self.create_function_button("ShowCsv", self.show_mult_csv)

        self.shot_similarity = self.create_function_button("Pace", self.frame_similarity)

        self.facerecognize = QPushButton("Face")
        self.facerecognize.clicked.connect(self.open_facerecognize_page)
        self.facerecognize.setMaximumWidth(80)

        # 输入框
        # frameconcat 输入框
        self.fc_st_input = self.create_function_lineEdit("start")
        self.fc_ed_input = self.create_function_lineEdit("end")

        # similarity 输入框
        self.sim_st_input = self.create_function_lineEdit("start")
        self.sim_ed_input = self.create_function_lineEdit("end")

        # metadata 输入框
        self.crew_st_input = self.create_function_lineEdit("Start")
        self.crew_ed_input = self.create_function_lineEdit("End")

        # 滑动条
        self.colorsSlider = QSlider(Qt.Horizontal, self)  # 水平方向
        self.colorsSlider.setMaximumWidth(80)
        self.colorsSlider.setMinimum(2)  # 设置最小值
        self.colorsSlider.setMaximum(20)  # 设置最大值
        self.colorsSlider.setSingleStep(1)  # 设置步长值
        self.colorsSlider.setValue(2)  # 设置当前值
        self.colorsSlider.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置，在下方
        self.colorsSlider.setTickInterval(1)  # 设置刻度间隔
        self.colorsSlider.valueChanged.connect(self.colorChange)

        self.frameConcatSlider = QSlider(Qt.Horizontal, self)  # 水平方向
        self.frameConcatSlider.setMaximumWidth(80)
        self.frameConcatSlider.setMinimum(5)  # 设置最小值
        self.frameConcatSlider.setMaximum(30)  # 设置最大值
        self.frameConcatSlider.setSingleStep(1)  # 设置步长值
        self.frameConcatSlider.setValue(10)  # 设置当前值
        self.frameConcatSlider.setTickPosition(QSlider.TicksBelow)  # 设置刻度位置，在下方
        self.frameConcatSlider.setTickInterval(5)  # 设置刻度间隔
        self.frameConcatSlider.valueChanged.connect(self.frameConcatChange)

        # 滑动条的显示
        self.labelColors = QLabel("2", self)
        self.labelColors.setFixedWidth(30)  # 预留固定宽度，支持最多3位数字

        self.labelFrameConcat = QLabel("10", self)
        self.labelFrameConcat.setFixedWidth(30)  # 同样预留固定宽度

        # 下拉框
        self.object_box = self.create_function_box(["shot", "keyFrame"])
        self.similarity_box = self.create_function_box(["single", "double"])

        # 创建一个网格布局，并将进度条和标签添加到网格中
        # 第零行，分镜+csv显示
        grid_layout.addWidget(self.shotcut, 0, 0)
        grid_layout.addWidget(self.show_csv, 0, 1)

        # 第一行，镜头拼接
        grid_layout.addWidget(self.fc_st_input, 1, 0)
        grid_layout.addWidget(self.fc_ed_input, 1, 1)
        grid_layout.addWidget(self.frameConcatSlider, 1, 2)
        grid_layout.addWidget(self.labelFrameConcat, 1, 3)
        grid_layout.addWidget(self.frameconcat, 1, 4)

        # 第二行，字幕
        grid_layout.addWidget(self.subtitle, 2, 0)
        grid_layout.addWidget(self.translate_button,2, 1)
        grid_layout.addWidget(self.intertitle, 2, 2)

        # 第三行，字幕卡
        grid_layout.addWidget(self.crew_st_input, 3, 0)
        grid_layout.addWidget(self.crew_ed_input, 3, 1)
        grid_layout.addWidget(self.credits, 3, 2)

        # 第四行，目标检测
        grid_layout.addWidget(self.object_box, 4, 0)
        grid_layout.addWidget(self.objects, 4, 1)
        grid_layout.addWidget(self.facerecognize, 4, 2)#修改

        # 第五行，shotscale
        grid_layout.addWidget(self.shotscale, 5, 0)

        # 第六行， Colors
        grid_layout.addWidget(self.colors, 6, 0)
        grid_layout.addWidget(self.colorsSlider, 6, 1)
        grid_layout.addWidget(self.labelColors, 6, 2)

        # 第七行 Pace 和 shotlenimgplot 处理区间[start, end]
        grid_layout.addWidget(self.sim_st_input, 7, 0)
        grid_layout.addWidget(self.sim_ed_input, 7, 1)
        grid_layout.addWidget(self.similarity_box, 7, 2)
        grid_layout.addWidget(self.shotlenimgplot, 7, 3)
        grid_layout.addWidget(self.shot_similarity, 7, 4)

        
        # 创建一个QWidget，将主布局设置为这个QWidget的布局
        widget = QWidget()
        widget.setLayout(grid_layout)
        self.setWidget(widget)

    def create_function_button(self, description, function):
        """创建功能按钮并绑定功能函数"""
        button = QPushButton(description, self)
        button.setMaximumWidth(80)  # 为了使得第二列button不会变成Slider的宽度，设定按钮的最大宽度
        button.clicked.connect(lambda: self.toggle_buttons(False))  # 禁用所有按钮
        button.clicked.connect(function)
        print(f"[Control] Button created: {description} -> {function.__name__}")
        return button

    def create_function_lineEdit(self, description):
        # 输入框
        input_box = QLineEdit(self)
        input_box.setPlaceholderText(description)

        # 设置输入框最大长度，避免输入过长
        input_box.setMaxLength(7)
        # 设置最大宽度
        input_box.setMaximumWidth(80)

        # 限制输入为 0 到 2000000 的数字
        # 使用更宽松的正则，允许逐步输入
        regex = QRegularExpression("^[0-9]*$")  # 允许 0 或多个数字
        validator = QRegularExpressionValidator(regex, input_box)
        input_box.setValidator(validator)

        return input_box

    def create_function_box(self, items):
        # 创建一个 QComboBox 下拉框
        combo_box = QComboBox()
        combo_box.setMaximumWidth(80)
        # 使用 for 循环将 items 中的每个项添加到下拉框
        for item in items:
            combo_box.addItem(item)

        # 返回创建好的 QComboBox
        return combo_box

    def toggle_buttons(self, enable):
        """启用或禁用所有按钮"""

        # 第零行
        self.shotcut.setEnabled(enable)
        self.show_csv.setEnabled(enable)

        # 第一行
        self.frameconcat.setEnabled(enable)

        # 第二行
        self.subtitle.setEnabled(enable)
        self.credits.setEnabled(enable)
        self.translate_button.setEnabled(enable)
        self.intertitle.setEnabled(enable)

        # 第三行
        self.objects.setEnabled(enable)
        self.facerecognize.setEnabled(enable)

        # 第四行
        self.shotscale.setEnabled(enable)

        # 第五行
        self.colors.setEnabled(enable)

        # 第六行
        self.shot_similarity.setEnabled(enable)
        self.shotlenimgplot.setEnabled(enable)

    
    def shotcut_toggle_buttons(self, enable, img_name:str="shotlength.png"):
        """启用或禁用所有按钮"""
        self.toggle_buttons(enable)
        
        # 在主线程中绘制图表（避免在子线程中调用 Matplotlib）
        if enable:
            try:
                from algorithms.resultSave import Resultsave
                rs = Resultsave(self.image_save + "/")
                # 读取 shot_len 数据
                shot_len_file = os.path.join(self.image_save, "video.txt")
                if os.path.exists(shot_len_file):
                    number = []
                    with open(shot_len_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            NumList = [int(n) for n in line.split()]
                            number.append(NumList[0])
                    
                    shot_len = []
                    start = -1
                    for idx, i in enumerate(number):
                        if idx == (len(number) - 1):
                            shot_len.append([start, i, i - start + 1])
                        elif idx != 0:
                            shot_len.append([start, i - 1, i - start])
                        start = i
                    
                    # 绘制图表
                    rs.plot_transnet_shotcut(shot_len)
                    print(f"[UI] Shot length chart saved to {self.image_save}")
            except Exception as exc:
                print(f"[UI] ERROR plotting shot length: {exc}")
        
        # 显示图片
        ImgPath = os.path.join(self.image_save, img_name)
        self.parent.analyze.add_tab_with_image(img_name[0:-4], ImgPath)
    
    def imageAnalyze_toggle_buttons(self, enable, img_name:str="colors.png"):
        """启用或禁用所有按钮"""
        self.toggle_buttons(enable)
        # 分析之后显示图片，传入路径即可
        ImgPath = os.path.join(self.image_save, img_name)
        self.parent.analyze.add_tab_with_image(img_name[0:-4], ImgPath)

    def subtitles_toggle_buttons(self, enable, img_name:str="subtitle_wc.png"):
        """启用或禁用所有按钮"""
        self.toggle_buttons(enable)
        ImgPath = os.path.join(self.image_save, img_name)
        self.parent.analyze.add_tab_with_image(img_name[0:-4], ImgPath)
    
    def translate_toggle_buttons(self, enable, img_name:str="translated.png"):
        """启用或禁用所有按钮（翻译完成）"""
        self.toggle_buttons(enable)
        # 翻译完成后不显示图片，因为翻译结果已经在字幕窗口显示
        print(f"[Translate] Translation finished, UI enabled")

    def intertitles_toggle_buttons(self, enable, img_name:str="intertitle.png"):
        """启用或禁用所有按钮"""
        self.toggle_buttons(enable)
        ImgPath = os.path.join(self.image_save, img_name)
        self.parent.analyze.add_tab_with_image(img_name[0:-4], ImgPath)

    def similarity_toggle_buttons(self, enable, image_names:str):
        """启用或禁用所有按钮"""
        self.toggle_buttons(enable)
        image_paths = [os.path.join(self.image_save, image_name) for image_name in image_names]
        image_window = ImageDialog(image_paths)
        image_window.exec_()
        similarity_ImgPath = os.path.join(self.image_save, image_names[0])
        self.parent.analyze.add_tab_with_image(image_names[0][1:-4], similarity_ImgPath)

    def credits_toggle_buttons(self, enable):
        """启用或禁用所有按钮"""
        self.toggle_buttons(enable)
        # 色彩分析之后显示3D图，传入路径即可
        colors_3D_ImgPath = os.path.join(self.image_save, "metadata.png")
        self.parent.analyze.add_tab_with_image("metadata", colors_3D_ImgPath)
    
    def on_filename_changed(self,filename):
        self.filename = filename
        # 使用用户目录下的绝对路径保存分析结果
        video_name = str(os.path.basename(self.filename)[0:-4])
        # 在用户 Documents 目录下创建 pyCinemetrics 文件夹
        base_dir = os.path.expanduser('~/Documents/pyCinemetrics')
        os.makedirs(base_dir, exist_ok=True)
        self.frame_save = os.path.join(base_dir, video_name, "frame")  # 图片存储路径
        self.image_save = os.path.join(base_dir, video_name)
        # 确保目录存在
        os.makedirs(self.frame_save, exist_ok=True)
        os.makedirs(self.image_save, exist_ok=True)
        self.toggle_buttons(True)

    '''
    功能模块写成if else 的原因是，在没有视频时或者在没有执行shotcut的情况下点击其他功能时，如果点击按钮，不希望所有按钮变成不能点击的灰色
    '''

    # 分镜 shot
    def shotcut_transNetV2(self):
        print(f"[DEBUG] shotcut_transNetV2 called, filename={self.filename}")
        if self.filename:
            # 分镜
            model = TransNetV2(self.filename, self)
            print(f"[DEBUG] TransNetV2 created, video_fn={model.video_fn}")
            # transNetV2_run(self.filename, self)
        else:
            print("[DEBUG] No filename, toggling buttons")
            self.shotcut_toggle_buttons(True)
            return
        # 分镜分析之后显示柱状图图，传入路径即可
        model.finished.connect(lambda: self.shotcut_toggle_buttons(True))
        print(f"[DEBUG] Creating pyqtbar, image_save={self.image_save}")
        bar = pyqtbar(model)

    # shot concat
    def getframeconcat(self):
        if not os.path.exists(self.frame_save):
            self.toggle_buttons(True)
            return
        st = self.fc_st_input.text()
        ed = self.fc_ed_input.text()

        if not st and not ed:
            self.show_warning("Error", f"Start and end cannot be empty!")
        elif not st:
            self.show_warning("Error", f"Start cannot be empty!")
        elif not ed:
            self.show_warning("Error", f"End cannot be empty!")
        elif int(st) < 0 or int(ed) >= self.parent.frameCnt or int(st) > int(ed):
            self.show_warning("Error", f"The values of start and end should belong to [0, {self.parent.frameCnt}), and start <= end!")
        else:
            concatframe_window = ConcatFrameWindow(self.frame_save, int(st), int(ed), self)
            concatframe_window.finished.connect(lambda: self.toggle_buttons(True))
            concatframe_window.exec_()

    # shot_len图颜色更改
    def plot_transnet_shotlength(self):
        st = self.sim_st_input.text()
        ed = self.sim_ed_input.text()
        plot_window = TransNetPlot(image_save_path=self.image_save,start=st,end=ed)
        plot_window.plotShotlen()  # 传递数据进行绘图
        plot_window.finished.connect(lambda: self.toggle_buttons(True))
        plot_window.exec_()  # 显示窗口


    # 字幕
    def __init__(self, parent, filename):
        super().__init__('Control', parent)
        self.parent = parent
        self.filename = filename
        self.AnalyzeImg = None
        self.AnalyzeImgPath = ""
        self.parent.filename_changed.connect(self.on_filename_changed)
        self.subtitleValue = 48    # 每多少帧检查一次字幕
        self.frameConcatValue = 10 # 拼接时每行的帧图个数
        self.facerecognize_window = None
        
        # 任务状态管理
        self._subtitle_task_running = False
        self._subtitle_processor = None
        
        self.init_ui()
    
    def _cleanup_subtitle_task(self):
        """清理字幕任务"""
        print("[Subtitles] Cleaning up subtitle task...")
        self._subtitle_task_running = False
        
        # 停止处理器
        if self._subtitle_processor and self._subtitle_processor.isRunning():
            print("[Subtitles] Stopping processor...")
            self._subtitle_processor.stop()
            self._subtitle_processor.wait(3000)
        
        self._subtitle_processor = None
        
        # 清理进度条引用
        if hasattr(self, '_subtitle_bar') and self._subtitle_bar:
            if hasattr(self._subtitle_bar, 'cleanup'):
                self._subtitle_bar.cleanup()
            self._subtitle_bar = None
        
        print("[Subtitles] Cleanup complete")
    
    def getsubtitles(self, filename=None):
        print(f"[Subtitles] Starting subtitle generation")
        
        # 检查是否有任务正在运行
        if self._subtitle_task_running:
            print("[Subtitles] ⚠️  Subtitle task already running!")
            self.show_warning("Warning", "Subtitle generation is already in progress!\nPlease wait for it to complete.")
            return
        
        # 检查是否有视频文件
        if not self.filename:
            print("[Subtitles] No video file loaded!")
            self.show_warning("Error", "No video file loaded!")
            return
        
        if not os.path.exists(self.image_save):
            print("[Subtitles] Image save path does not exist!")
            self.toggle_buttons(True)
            return
        
        # 标记任务正在运行
        self._subtitle_task_running = True
        
        # 创建处理器
        self._subtitle_processor = SubtitleProcessorWhisper(self.filename, self.image_save, self.parent)
        
        # 连接信号
        self._subtitle_processor.subtitlesignal.connect(self.parent.subtitle.textSubtitle.setPlainText)
        self._subtitle_processor.finished.connect(self._on_subtitle_finished)
        
        # 创建进度条
        bar = pyqtbar(self._subtitle_processor)
        self._subtitle_bar = bar  # 保持引用
        print(f"[Subtitles] Processor started, progress bar created")
    
    def _on_subtitle_finished(self, success):
        """字幕任务完成后的清理"""
        print(f"[Subtitles] Task finished (success={success})")
        self._cleanup_subtitle_task()
        self.subtitles_toggle_buttons(True)
    
    def translate_srt(self):
        # save_path = r"./img/" + imgpath + "/"
        # input_srt_file = save_path+"subtitle.srt"
        input_srt_file = self.image_save + "/subtitle.srt"

        print(f"[Translate] Starting translation for: {input_srt_file}")

        # Create the TranslateSrtProcessor instance
        translate_processor = TranslateSrtProcessor(input_srt_file, self.image_save, self)
        translate_processor.subtitlesignal.connect(self.parent.subtitle.textSubtitle.setPlainText)
        translate_processor.finished.connect(lambda: self.translate_toggle_buttons(True))

        # 创建进度条
        bar = pyqtbar(translate_processor)
        # 保持 bar 的引用，防止被垃圾回收
        self._translate_bar = bar
        print(f"[Translate] Processor started, progress bar created: {bar}")
    
    # 演职员表
    def getcredits(self, filename):
        if not os.path.exists(self.frame_save):
            self.toggle_buttons(True)
            return

        st = self.crew_st_input.text()
        ed = self.crew_ed_input.text()

        if not st and not ed:
            self.show_warning("Error", f"Start and end cannot be empty!")
        elif not st:
            self.show_warning("Error", f"Start cannot be empty!")
        elif not ed:
            self.show_warning("Error", f"End cannot be empty!")
        elif int(st) < 0 or int(ed) >= self.parent.frameCnt or int(st) > int(ed):
            self.show_warning("Error", f"The values of start and end should belong to [0, {self.parent.frameCnt}), and start <= end!")
        else:
            # 动态导入 CrewProcessor
            try:
                from algorithms.metaData import CrewProcessor
                creditsprocesser = CrewProcessor(self.filename, self.image_save, self.subtitleValue, self.parent,st=int(st),ed=int(ed))
                creditsprocesser.Crewsignal.connect(self.parent.subtitle.textSubtitle.setPlainText)
                creditsprocesser.finished.connect(lambda: self.credits_toggle_buttons(True))
                bar = pyqtbar(creditsprocesser)
                print(f"[MetaData] Processor started with progress bar")
            except ImportError as e:
                print(f"[MetaData] ERROR: {e}")
                self.show_warning(
                    "PaddleOCR Unavailable",
                    "PaddleOCR is currently unavailable due to a dependency conflict (SSL module). "
                    "This is a known limitation. The feature may work in a future update."
                )
                self.credits_toggle_buttons(True)



    # 字幕卡
    def getintertitle(self,filename):
        if os.path.exists(self.image_save):
            # 动态导入 InterTitle
            try:
                from algorithms.interTitle import InterTitle
                intertitle = InterTitle(self.filename, self.image_save, self.subtitleValue, self.parent)
                intertitle.intertitlesignal.connect(self.parent.subtitle.textSubtitle.setPlainText)
                intertitle.finished.connect(lambda: self.intertitles_toggle_buttons(True))
                bar = pyqtbar(intertitle)
            except ImportError as e:
                print(f"[Intertitle] ERROR: {e}")
                self.show_warning(
                    "PaddleOCR Unavailable",
                    "PaddleOCR is currently unavailable due to a dependency conflict. "
                    "This is a known issue with the SSL module. The feature will be available in a future update."
                )
                self.intertitles_toggle_buttons(True)
        else:
            self.toggle_buttons(True)
            return

    # 目标检测
    def object_detect(self):
        if os.path.exists(self.image_save):
            objectdetection = ObjectDetection(self.filename, self.image_save, self.object_box.currentIndex())
        else:
            self.toggle_buttons(True)
            return

        objectdetection.finished.connect(lambda: self.imageAnalyze_toggle_buttons(True, "wordcloud_ch.png"))
        bar = pyqtbar(objectdetection)

    # ShotScale
    def getshotscale(self):
        if os.path.exists(self.frame_save):
            #csv_file = self.image_save + "shotscale.csv"
            shotscaleclass = ShotScale(25, self.image_save, self.frame_save)
        else:
            self.toggle_buttons(True)
            return

        shotscaleclass.finished.connect(lambda: self.imageAnalyze_toggle_buttons(True, "shotscale.png"))
        #万一视频名字不变内容变了呢？
        #if not os.path.exists(csv_file):
        png_file = self.image_save + "shotscale.png"
        self.AnalyzeImgPath = png_file
        self.AnalyzeImg = QPixmap(self.AnalyzeImgPath)
        self.AnalyzeImg = self.AnalyzeImg.scaled(300,250)
        bar = pyqtbar(shotscaleclass)
        # self.toggle_button.setVisible(False)  # 初始时不显示按钮
    
    # 颜色分析
    def colorAnalyze(self):
        if os.path.exists(self.frame_save):
            imgpath = os.path.basename(self.filename)[0:-4]
            coloranalysis = ColorAnalysis("", imgpath, self.parent.colorsC, image_save_path=self.image_save)
        else:
            self.imageAnalyze_toggle_buttons(True, "colors.png")
            return
        # 在 UI 线程中绘制 3D 图
        coloranalysis.finished.connect(lambda: self.color_finish_handler(imgpath))
        bar = pyqtbar(coloranalysis)
    
    def color_finish_handler(self, imgpath):
        """颜色分析完成后的处理（在 UI 线程中）"""
        try:
            from algorithms.resultSave import Resultsave
            # 使用绝对路径
            rs = Resultsave(self.image_save)
            # 读取 CSV 数据并绘制 3D 图
            csv_file = os.path.join(self.image_save, "colors.csv")
            if os.path.exists(csv_file):
                import pandas as pd
                df = pd.read_csv(csv_file)
                # CSV 格式：FrameId,Color0,Color1 （十六进制格式如 #63686B）
                allcolors_rgb_list = []
                color_cols = [col for col in df.columns if col.startswith('Color')]
                
                for _, row in df.iterrows():
                    for col in color_cols:
                        color_val = row[col]
                        # 解析十六进制颜色值 "#RRGGBB" -> [R, G, B]
                        if isinstance(color_val, str) and color_val.startswith('#'):
                            hex_color = color_val[1:]  # 去掉 #
                            if len(hex_color) == 6:
                                r = int(hex_color[0:2], 16)
                                g = int(hex_color[2:4], 16)
                                b = int(hex_color[4:6], 16)
                                allcolors_rgb_list.append([r, g, b])
                        elif isinstance(color_val, str):
                            try:
                                import ast
                                rgb = ast.literal_eval(color_val)
                                if isinstance(rgb, (list, tuple)) and len(rgb) == 3:
                                    allcolors_rgb_list.append(list(rgb))
                            except:
                                pass
                
                if allcolors_rgb_list:
                    # plot_scatter_3d 期望嵌套列表格式：[[[R,G,B], [R,G,B]], [[R,G,B]]]
                    # 我们需要将每个帧的颜色分组
                    rs.plot_scatter_3d([allcolors_rgb_list])
                    print(f"[UI] 3D scatter plot saved with {len(allcolors_rgb_list)} colors")
                    
                    # 在 Analyse 标签页显示 3D 图
                    scatter_3d_path = os.path.join(self.image_save, "scatter_3d.png")
                    if os.path.exists(scatter_3d_path):
                        self.parent.analyze.add_tab_with_image("colors_3d", scatter_3d_path)
                        print(f"[UI] Added 3D scatter tab")
                else:
                    print(f"[UI] No valid colors found in CSV")
        except Exception as exc:
            print(f"[UI] ERROR plotting 3D scatter: {exc}")
            import traceback
            traceback.print_exc()
        
        # 更新 UI
        self.imageAnalyze_toggle_buttons(True, "colors.png")
        
    #  滚动条变化
    def colorChange(self):
        # print("current Color Category slider value:"+str(self.colorsSlider.value()))
        self.labelColors.setText(str(self.colorsSlider.value()))
        self.parent.colorsC = self.colorsSlider.value()

    def frameConcatChange(self):
        # print("current frameconcat size Category slider value:" + str(self.frameConcatSlider.value()))
        self.frameConcatValue = self.frameConcatSlider.value()
        self.labelFrameConcat.setText(str(self.frameConcatValue))
    
    # 弹框显示单个csv文件
    # def show_csv(self, csv_filename):
    #     csv_path = os.path.join(self.image_save, csv_filename)
    #     if not os.path.exists(csv_path):
    #         # Show a warning message if the file doesn't exist
    #         self.show_warning("File Not Found", f"The file at {csv_path} does not exist.")
    #     else:
    #         csv_dialog = CsvViewerDialog(csv_path)
    #         csv_dialog.finished.connect(lambda: self.toggle_buttons(True))
    #         csv_dialog.exec()
    
    # 显示多个csv文件
    def show_mult_csv(self):
        if not os.path.exists(self.image_save):
            # Show a warning message if the file doesn't exist
            self.show_warning("File Not Found", f"The file at {self.image_save} does not exist.")
        else:
            mult_csv_dialog = MultiCsvViewerDialog(self.image_save)
            mult_csv_dialog.finished.connect(lambda: self.toggle_buttons(True))
            mult_csv_dialog.exec()

    # 弹出警告框
    def show_warning(self, title, message):
        """ Show a warning message box """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.finished.connect(lambda: self.toggle_buttons(True))
        msg_box.exec()

    # 图片相似度
    def frame_similarity(self):
        if os.path.exists(self.filename):
            st = self.sim_st_input.text()
            ed = self.sim_ed_input.text()
            

            if not st and not ed:
                self.show_warning("Error", f"Start and end cannot be empty!")
            elif not st:
                self.show_warning("Error", f"Start cannot be empty!")
            elif not ed:
                self.show_warning("Error", f"End cannot be empty!")
            elif int(st) < 0 or int(ed) >= self.parent.frameCnt or int(st) > int(ed):
                self.show_warning("Error", f"The values of start and end should belong to [0, {self.parent.frameCnt}), and start <= end!")
            else:
                similarity = Similarity(self.filename, int(st), int(ed), self.similarity_box.currentIndex())
                image_names = np.array(["pace.png", "pace_reversed.png"])
                similarity.finished.connect(lambda: self.similarity_toggle_buttons(True, image_names))
                bar = pyqtbar(similarity)
        else:
            self.toggle_buttons(True)
            return

    # 人脸识别
    def open_facerecognize_page(self):
        """打开子页面"""
        if self.object_box.currentIndex() == 0:
            input_images_dir = self.frame_save # 输入图片文件夹
        elif self.object_box.currentIndex() == 1:
            input_images_dir = self.image_save  + "/ImagetoText"# 输入图片文件夹

        image_folder = self.image_save + "/faceRecognition"
        # 如果子页面已存在，置顶并激活
        if self.facerecognize_window is not None:
            self.facerecognize_window.raise_()
            self.facerecognize_window.activateWindow()
            return

        if os.path.exists(input_images_dir):
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            self.facerecognize_window = MappingApp(image_folder, input_images_dir, self.parent, self.filename)
            self.facerecognize_window.setModal(False)
            self.facerecognize_window.show()
        else:
            self.toggle_buttons(True)
            return

        # 在子页面关闭时释放标志
        self.facerecognize_window.finished.connect(self.on_child_window_closed)
    
    def on_child_window_closed(self):
        """子页面关闭时重置标志"""
        self.facerecognize_window = None

        
        
        
