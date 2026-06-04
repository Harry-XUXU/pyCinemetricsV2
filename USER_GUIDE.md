# PyCinemetrics V2 使用指南 / User Guide

**版本 / Version**: 1.0.0  
**更新日期 / Last Updated**: 2025-03-19

---

## 目录 / Table of Contents

- [概述 / Overview](#概述--overview)
- [系统要求 / System Requirements](#系统要求--system-requirements)
- [安装与配置 / Installation & Configuration](#安装与配置--installation--configuration)
- [界面介绍 / Interface Overview](#界面介绍--interface-overview)
- [功能说明 / Features](#功能说明--features)
- [模型管理 / Model Management](#模型管理--model-management)
- [常见问题 / FAQ](#常见问题--faq)

---

## 概述 / Overview

**PyCinemetrics V2** 是一款专业的电影视频分析工具，专为电影研究者、剪辑师和影视爱好者设计。它可以自动分析视频的分镜、字幕、颜色、景别、人物等元素，并生成详细的分析报告。

**PyCinemetrics V2** is a professional cinematic video analysis tool designed for film researchers, editors, and cinephiles. It automatically analyzes shots, subtitles, colors, shot scales, faces, and other elements, generating detailed analytical reports.

### 主要功能 / Key Features

| 功能 / Feature | 说明 / Description |
|---|---|
| 🎬 分镜检测 / Shot Detection | 自动检测视频中的镜头切换点 | Automatically detect shot transitions |
| 📊 分镜长度分析 / Shot Length | 生成每个镜头的时长统计图表 | Generate duration statistics for each shot |
| 🎞️ 帧图拼接 / Frame Mosaic | 将分镜帧拼接为全景图 | Create panoramic view of shot frames |
| 📝 字幕识别 / Subtitle Recognition | 自动识别视频中的语音为字幕 | Automatic speech-to-text transcription |
| 🌐 字幕翻译 / Subtitle Translation | 将英文字幕翻译为中文 | Translate English subtitles to Chinese |
| 🎨 颜色分析 / Color Analysis | 分析每帧的颜色分布 | Analyze color distribution per frame |
| 📏 景别分析 / Shot Scale | 识别远景、全景、中景、近景、特写 | Identify long shot, full shot, medium shot, close-up |
| 👤 人物识别 / Face Recognition | 识别视频中的人物面部 | Detect and recognize faces in video |
| 🏷️ 目标检测 / Object Detection | 检测视频中的物体和场景 | Detect objects and scenes in video |
| 📋 演职员表 / Credits | 识别片尾演职员表 | Recognize end credits |
| 🎬 幕间标题 / Intertitle | 识别电影中的幕间标题 | Detect intertitles in films |
| 📈 节奏分析 / Pace Analysis | 分析镜头切换节奏 | Analyze shot transition rhythm |

---

## 系统要求 / System Requirements

### macOS
- **操作系统 / OS**: macOS 10.15 (Catalina) 或更高版本
- **处理器 / Processor**: Apple Silicon (M1/M2/M3) 或 Intel x86_64
- **内存 / RAM**: 8GB 以上推荐
- **磁盘空间 / Storage**: 至少 5GB 可用空间（不含模型文件）

### 模型文件 / Model Files
- TransNetV2 模型: ~200MB
- Whisper 模型: ~500MB
- OpenPose 模型: ~250MB
- 翻译模型: ~300MB

---

## 安装与配置 / Installation & Configuration

### 1. 下载应用 / Download App

从发布页面下载 `pyCinemetricsV2.app` 或 `pyCinemetricsV2.dmg`。

Download `pyCinemetricsV2.app` or `pyCinemetricsV2.dmg` from the release page.

### 2. 首次运行 / First Run

```bash
# 如果 macOS 阻止运行，请在终端执行：
# If macOS blocks the app, run in Terminal:
xattr -d com.apple.quarantine /path/to/pyCinemetricsV2.app

# 然后双击打开应用
# Then double-click to open the app
```

### 3. 模型配置 / Model Configuration

首次启动时，软件会检查必需的模型文件。如果模型缺失，请按以下步骤配置：

On first launch, the app checks for required model files. If models are missing, follow these steps:

1. 点击菜单栏 **Settings > Model Paths**
2. 选择模型文件夹位置
3. 推荐将模型放在：`~/Documents/pyCinemetrics/models/`

**模型目录结构 / Model Directory Structure**:

```
~/Documents/pyCinemetrics/models/
├── transnetv2-weights/          # TransNetV2 分镜模型
│   ├── saved_model.pb
│   └── variables/
├── faster-whisper-small/        # Whisper 字幕模型
│   ├── config.json
│   └── model.bin
├── pose/                        # OpenPose 景别模型
│   ├── body_25/
│   │   ├── pose_deploy.prototxt
│   │   └── pose_iter_584000.caffemodel
│   └── coco/
│       ├── pose_deploy_linevec.prototxt
│       └── pose_iter_440000.caffemodel
└── opus-mt-en-zh/               # 翻译模型
    ├── config.json
    └── pytorch_model.bin
```

### 4. 配置文件 / Configuration File

配置保存在：`~/.pyCinemetricsV2.json`

Configuration saved at: `~/.pyCinemetricsV2.json`

---

## 界面介绍 / Interface Overview

```
┌─────────────────────────────────────────────────────────────┐
│  File    Help                           [PyCinemetrics V2]  │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  信息    │              VLC 视频播放器                       │
│  字幕    │              (VLC Video Player)                   │
│          │                                                  │
│          │                                                  │
│          │                                                  │
│          │                                                  │
├──────────┴──────────────────────────────────────────────────┤
│                    时间轴 / Timeline                         │
│                 (帧缩略图 / Frame Thumbnails)                │
├────────────────────────────────┬────────────────────────────┤
│                                │                            │
│                                │    功能按钮 /              │
│                                │    Control Panel           │
│                                │                            │
│                                │    Shot  Subtitles         │
│                                │    Colors  Face            │
│                                │    ...                     │
│                                │                            │
└────────────────────────────────┴────────────────────────────┘
```

### 面板说明 / Panel Description

| 面板 / Panel | 位置 / Position | 功能 / Function |
|---|---|---|
| 信息 / Info | 左侧 / Left | 显示视频基本信息 | Video information |
| 字幕 / Subtitle | 左侧 / Left | 显示识别和翻译的字幕 | Display subtitles |
| 控制 / Control | 右侧 / Right | 功能按钮面板 | Function buttons |
| 分析 / Analyze | 右侧 / Right | 分析结果图表 | Analysis charts |
| 时间轴 / Timeline | 底部 / Bottom | 帧缩略图导航 | Frame navigation |

---

## 功能说明 / Features

### 1. 分镜检测 / Shot Detection

**按钮 / Button**: `Shot`

自动检测视频中的镜头切换点，生成每个镜头的起始和结束帧。

Automatically detect shot transitions, generating start and end frames for each shot.

**使用方法 / How to Use**:
1. 打开视频 / Open a video
2. 点击 **Shot** 按钮
3. 等待分析完成（进度条显示）
4. 结果保存在 `~/Documents/pyCinemetrics/<视频名>/`

**输出 / Output**:
- `shotcut.csv` - 分镜数据（起始帧、结束帧、长度）
- `shotlength.png` - 分镜长度柱状图
- 分镜帧图片保存在 `frame/` 文件夹

---

### 2. 分镜长度图表 / Shot Length Plot

**按钮 / Button**: `Shotlength`

生成分镜长度的可视化柱状图。

Generate a bar chart visualization of shot lengths.

**输出 / Output**: `shotlength.png`

---

### 3. 帧图拼接 / Frame Mosaic

**按钮 / Button**: `Mosaic`

将分镜帧拼接成全景图，方便快速浏览所有关键帧。

Create a panoramic view of all key frames for quick browsing.

**使用方法 / How to Use**:
1. 先执行分镜检测 / Run Shot Detection first
2. 设置起始和结束帧号（可选）/ Set start/end frame (optional)
3. 点击 **Mosaic** 按钮
4. 在弹出的窗口中查看拼接结果

**参数 / Parameters**:
- Start: 起始帧号 / Start frame number
- End: 结束帧号 / End frame number
- 默认拼接所有分镜帧 / Default: mosaic all shot frames

---

### 4. 字幕识别 / Subtitle Recognition

**按钮 / Button**: `Subtitles`

使用 Whisper 模型自动识别视频中的语音，生成字幕文件。

Use Whisper model to automatically transcribe speech to subtitles.

**使用方法 / How to Use**:
1. 确保已配置 Whisper 模型 / Ensure Whisper model is configured
2. 点击 **Subtitles** 按钮
3. 等待识别完成（较长视频需要较长时间）

**输出 / Output**:
- `subtitle.srt` - SRT 格式字幕文件
- `subtitle.csv` - CSV 格式字幕数据
- `subtitle_wc.png` - 字幕词云图

---

### 5. 字幕翻译 / Subtitle Translation

**按钮 / Button**: `Translate`

将英文字幕翻译为中文。

Translate English subtitles to Chinese.

**使用方法 / How to Use**:
1. 先执行字幕识别 / Run Subtitle Recognition first
2. 点击 **Translate** 按钮
3. 等待翻译完成

**输出 / Output**:
- `translated.srt` - 翻译后的 SRT 字幕
- `translated.csv` - 翻译后的 CSV 数据

---

### 6. 颜色分析 / Color Analysis

**按钮 / Button**: `Colors`

分析视频中每帧的颜色分布，生成颜色饼图和 3D 散点图。

Analyze color distribution per frame, generating pie charts and 3D scatter plots.

**使用方法 / How to Use**:
1. 先执行分镜检测 / Run Shot Detection first
2. 点击 **Colors** 按钮
3. 等待分析完成

**输出 / Output**:
- `colors.csv` - 颜色数据
- `colors.png` - 颜色饼图
- `scatter_3d.png` - 3D 颜色散点图

---

### 7. 景别分析 / Shot Scale Analysis

**按钮 / Button**: `ShotScale`

使用 OpenPose 人体姿态估计，识别每个分镜的景别类型。

Use OpenPose pose estimation to identify shot scale types.

**景别类型 / Shot Scale Types**:
- Empty Shot - 空景（无人物）
- Long Shot - 远景
- Full Shot - 全景
- Medium Shot - 中景
- Medium Close-Up - 近景
- Close-Up - 特写

**输出 / Output**:
- `shotscale.csv` - 景别数据
- `shotscale.png` - 景别饼图

---

### 8. 人物识别 / Face Recognition

**按钮 / Button**: `Face`

识别视频中的人物面部，支持面部检测和特征提取。

Detect and extract facial features from video.

**使用方法 / How to Use**:
1. 点击 **Face** 按钮
2. 在弹出的窗口中查看识别结果
3. 支持设置面部识别阈值

---

### 9. 目标检测 / Object Detection

**按钮 / Button**: `image2Text`

使用 OCR 技术检测视频帧中的文字和物体。

Use OCR to detect text and objects in video frames.

**输出 / Output**: 检测结果文本 / Detection results text

---

### 10. 演职员表识别 / Credits Recognition

**按钮 / Button**: `MetaData`

识别片尾演职员表中的信息。

Recognize end credits information.

**使用方法 / How to Use**:
1. 先执行分镜检测 / Run Shot Detection first
2. 设置起始和结束帧号 / Set start/end frame
3. 点击 **MetaData** 按钮

---

### 11. 幕间标题识别 / Intertitle Recognition

**按钮 / Button**: `Intertitle`

识别电影中的幕间标题（如章节标题、时间地点说明等）。

Detect intertitles (chapter titles, time/place descriptions).

---

### 12. 节奏分析 / Pace Analysis

**按钮 / Button**: `Pace`

分析镜头切换的节奏和频率。

Analyze shot transition rhythm and frequency.

**输出 / Output**: 节奏分析图表 / Pace analysis chart

---

### 13. CSV 查看器 / CSV Viewer

**按钮 / Button**: `ShowCsv`

查看和比较多个分析结果 CSV 文件。

View and compare multiple analysis result CSV files.

---

## 模型管理 / Model Management

### 配置模型路径 / Configure Model Paths

1. 点击菜单栏 **Settings > Model Paths**
2. 为每个模型选择对应的文件夹
3. 点击 **OK** 保存配置

### 重置模型路径 / Reset Model Paths

在模型设置对话框中点击 **Reset to Default**，清除所有自定义路径。

Click **Reset to Default** in the model settings dialog to clear all custom paths.

### 模型优先级 / Model Path Priority

软件按以下顺序查找模型：

The app searches for models in the following order:

1. 用户配置路径（Settings 中设置的路径）
2. 用户目录（`~/Documents/pyCinemetrics/models/`）
3. 打包目录（应用内置的模型）
4. 开发目录（项目根目录的 models/）

---

## 常见问题 / FAQ

### Q1: 打开应用时提示"无法验证开发者"怎么办？

**A**: macOS 安全设置会阻止未签名的应用。解决方法：

```bash
xattr -d com.apple.quarantine /path/to/pyCinemetricsV2.app
```

或在 **系统偏好设置 > 安全性与隐私** 中允许运行。

### Q2: 分析进度条卡住不动？

**A**: 
- 对于长视频（超过 1 小时），分析需要较长时间，请耐心等待
- 分镜检测完成后，时间轴不会自动加载所有帧（避免 UI 卡顿）
- 使用 **ShowCsv** 按钮查看分析结果

### Q3: 模型文件在哪里下载？

**A**: 
- TransNetV2: https://github.com/soCzech/TransNetV2
- Whisper: 使用 faster-whisper 库自动下载
- OpenPose: 从 OpenPose 官方仓库获取
- 翻译模型: 从 Hugging Face 下载 opus-mt-en-zh

### Q4: 分析结果保存在哪里？

**A**: 所有分析结果保存在：

```
~/Documents/pyCinemetrics/<视频名>/
├── frame/           # 分镜帧图片
├── shotcut.csv      # 分镜数据
├── shotlength.png   # 分镜长度图
├── subtitle.srt     # 字幕文件
├── colors.csv       # 颜色数据
├── shotscale.csv    # 景别数据
└── ...
```

### Q5: 如何调整分析参数？

**A**: 
- 字幕检查间隔：修改 `subtitleValue`（默认每 48 帧检查一次）
- 帧拼接数量：修改 `frameConcatValue`（默认每行 10 帧）
- 颜色数量：修改 `colorsC`（默认 2 种颜色）

### Q6: 支持哪些视频格式？

**A**: 支持所有 VLC 播放器支持的视频格式，包括：
- MP4, MKV, AVI, MOV, WMV, FLV
- 各种编码格式（H.264, H.265, VP9 等）

### Q7: 可以在 Linux/Windows 上运行吗？

**A**: 当前版本仅支持 macOS。Linux 和 Windows 版本正在开发中。

---

## 输出文件说明 / Output Files Reference

| 文件名 / Filename | 说明 / Description | 来源 / Source |
|---|---|---|
| `shotcut.csv` | 分镜数据 | Shot Detection |
| `shotlength.png` | 分镜长度柱状图 | Shot Length |
| `video.txt` | 分镜帧号列表 | Shot Detection |
| `subtitle.srt` | SRT 字幕文件 | Subtitle Recognition |
| `subtitle.csv` | 字幕数据 | Subtitle Recognition |
| `subtitle_wc.png` | 字幕词云 | Subtitle Recognition |
| `translated.srt` | 翻译后字幕 | Translation |
| `translated.csv` | 翻译后数据 | Translation |
| `colors.csv` | 颜色数据 | Color Analysis |
| `colors.png` | 颜色饼图 | Color Analysis |
| `scatter_3d.png` | 3D 颜色散点图 | Color Analysis |
| `shotscale.csv` | 景别数据 | Shot Scale |
| `shotscale.png` | 景别饼图 | Shot Scale |
| `metadata.png` | 演职员表图片 | Credits |

---

## 快捷键 / Keyboard Shortcuts

| 快捷键 / Shortcut | 功能 / Function |
|---|---|
| `Cmd+O` | 打开视频 / Open video |
| `Space` | 播放/暂停 / Play/Pause |
| `←/→` | 快退/快进 / Seek backward/forward |
| `F` | 全屏切换 / Toggle fullscreen |

---

## 技术支持 / Support

- **问题反馈 / Bug Reports**: 提交 Issue 到项目仓库
- **功能建议 / Feature Requests**: 提交 Feature Request
- **使用帮助 / Help**: 查看本指南或联系开发者

---

## 许可证 / License

详见 `LICENSE.txt` 文件。

See `LICENSE.txt` for details.

---

*最后更新 / Last Updated: 2025-03-19*
