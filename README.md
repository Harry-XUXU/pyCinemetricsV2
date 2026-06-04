# pyCinemetrics_V2.0 
[![CI Build](https://github.com/CBD-Lab/pyCinemetricsV2/actions/workflows/ci.yml/badge.svg)](https://github.com/CBD-Lab/pyCinemetricsV2/actions/workflows/ci.yml)

> **🍎 macOS 移植版** — 本 Fork 为原始项目增加了完整的 macOS 适配与 PyInstaller 打包方案。
> 上游仓库：[CBD-Lab/pyCinemetricsV2](https://github.com/CBD-Lab/pyCinemetricsV2)

## macOS 移植说明

本 Fork 在原始项目基础上完成了以下工作：

### 兼容性修复
- **multiprocessing 修复** — macOS 上 PyInstaller 打包后子进程重启 App 的问题
- **工作目录自动切换** — App Bundle 环境下自动定位资源文件
- **matplotlib 线程安全** — 图表渲染从子线程迁至主线程，解决 macOS 上偶发崩溃
- **延迟导入** — 避免 PyInstaller 打包时 SSL 模块冲突

### 路径管理
- 输出路径从 `./img/` 改为 `~/Documents/pyCinemetrics/`
- 新增**模型路径设置 GUI 对话框**（Settings → Model Path）

### 打包方案
- PyInstaller `.spec` 配置 + 自动化打包脚本
- DMG 安装包生成
- macOS 代码签名与环境变量注入（`Info.plist`）
- 详细打包文档：[MACOS_BUILD_GUIDE.md](MACOS_BUILD_GUIDE.md)

### 快速开始（macOS）
```bash
# 开发环境
pip install -r requirements.txt
python main.py

# 打包为 .app
./build_macos.sh
open dist/pyCinemetricsV2.app
```

---

## Paper
### https://www.sciencedirect.com/science/article/pii/S2352711025002651

title = {PyCinemetricsV2: Interactive computational film software based on transformers and PySide6},
journal = {SoftwareX},
volume = {31},
pages = {102299},
year = {2025},
issn = {2352-7110},
doi = {https://doi.org/10.1016/j.softx.2025.102299},
url = {https://www.sciencedirect.com/science/article/pii/S2352711025002651},
author = {Chunfang Li and Yalv Fan and Yushi Shen and Kun Wang and Yuhe Hu and Fei Zhang and Yuchen Pei and Tongtong Zheng and Zhuoqi Shi}

## English Version

1. After cloning, the only missing folder is `models`. After downloading the `models` folder from the cloud drive, just place it in the directory, and it will run.
2. Files shared through the cloud drive: 
    Model files and test_videos:
   - Link: [Baidu Netdisk](https://pan.baidu.com/s/1GMlOYvglimvSoIcIowuM0A?pwd=1234), [Google Drive](https://drive.google.com/drive/folders/1ho48Bx6KF-fZewnwBpoHmdI5F1XCY6Xm?usp=sharing)  
3. Model and functionality correspondences:
    - Video boundary detection: transnetv2
    - Face recognition: buffalo_l
    - Speech-to-text subtitles: faster-whisper-base
    - Subtitle detection：paddleocr
    - Object detection: git-base
    - Translation: opus-mt-en-zh
    - Shot type recognition：pose net
4. Potential issues:
    - If `pip install insightface` fails, please install it manually. [Link to GitHub](https://github.com/Gourieff/Assets/tree/main/Insightface)
    - Some models are outdated, so the latest numpy cannot be used. Version 1.26.0 is compatible.
5.License:
    - This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License (LGPL) as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.
---

## 中文版本

1. clone之后仅缺少`models`文件夹，网盘下载`models`文件夹后放进目录即可运行。
2. 通过网盘分享的文件：
    模型文件和测试视频：
   - 链接: [Baidu Netdisk](https://pan.baidu.com/s/1GMlOYvglimvSoIcIowuM0A?pwd=1234), [Google Drive](https://drive.google.com/drive/folders/1ho48Bx6KF-fZewnwBpoHmdI5F1XCY6Xm?usp=sharing)  
3. 模型与功能对应
    - 视频边界检测：transnetv2
    - 人脸识别：buffalo_l
    - 语音识别字幕：faster-whisper-base
    - 字幕检测：paddleocr
    - 目标检测：git-base
    - 翻译： opus-mt-en-zh
    - 镜头类型识别：pose net
4. 可能会遇到的问题
    - 如果pip install insightface出错，请手动安装。 [Link to GitHub](https://github.com/Gourieff/Assets/tree/main/Insightface)
    - 因为有些模型比较旧，所以不能使用最新的numpy，1.26.0是可用的。

软件
https://pan.baidu.com/s/1_4PZGLwli_wLjY3xEPO6uQ?pwd=2025 提取码: 2025
<img width="800" height="1012" alt="9ac7776c3366e486298be65a52ceeed7" src="https://github.com/user-attachments/assets/b37b9cb9-7638-45f8-a784-5963964a9e61" />

<img width="750" height="550" alt="50ff759fd78f1d684c02dac4daea9502" src="https://github.com/user-attachments/assets/4371936e-758f-4fac-afea-aa95e7b043ca" />

