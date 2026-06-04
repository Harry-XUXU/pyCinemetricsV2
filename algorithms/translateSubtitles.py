import os
import sys
import torch
import csv
import re
from transformers import MarianMTModel, MarianTokenizer
from ui.progressBar import *


class TranslateSrtProcessor(QThread):
    signal = Signal(int, int, int, str)
    subtitlesignal = Signal(str)
    finished = Signal(bool)

    def __init__(self, srt_path, save_path, parent, src_lang='en', target_lang='zh'):
        super(TranslateSrtProcessor, self).__init__()
        self.srt_path = srt_path
        self.save_path = save_path
        self.output_srt_file = os.path.join(self.save_path, 'translated.srt')
        self.output_csv_file = os.path.join(self.save_path, 'translated.csv')
        self.parent = parent

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # 使用绝对路径解决 open 启动时工作目录问题
        if getattr(sys, 'frozen', False):
            # 打包环境：使用 sys.executable 的目录
            executable_dir = os.path.dirname(sys.executable)
            # 如果在 .app bundle 内，资源在 Resources 目录
            if executable_dir.endswith('.app/Contents/MacOS'):
                resources_dir = os.path.join(os.path.dirname(executable_dir), 'Resources')
                self.model_name = os.path.join(resources_dir, 'models', 'opus-mt-en-zh')
            else:
                self.model_name = os.path.join(executable_dir, 'models', 'opus-mt-en-zh')
        else:
            # 开发环境
            self.model_name = os.path.abspath("./models/opus-mt-en-zh")
        
        print(f"[Translate] Loading model from: {self.model_name}")
        self.model = MarianMTModel.from_pretrained(self.model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        self.model.to(self.device)

    def run(self):
        # Read the input SRT file
        with open(self.srt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        translated_lines = []
        csv_data = []
        translated_text = ""
        time_pattern = r"(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})"

        # 计算总行数用于进度条
        total_lines = len(lines)
        print(f"[Translate] Processing {total_lines} lines...")

        # Process each line
        for i, line in enumerate(lines):
            # 发送进度信号
            progress = int((i / total_lines) * 100)
            self.signal.emit(progress, i, total_lines, f"Translating: {i}/{total_lines}")

            # Extract timestamps
            time_match = re.match(time_pattern, line.strip())
            if time_match:
                start_time = int(time_match.group(1)) * 3600 + int(time_match.group(2)) * 60 + int(
                    time_match.group(3)) + int(time_match.group(4)) / 1000
                end_time = int(time_match.group(5)) * 3600 + int(time_match.group(6)) * 60 + int(
                    time_match.group(7)) + int(time_match.group(8)) / 1000
                translated_lines.append(line)  # Keep the original timestamp

            elif "-->" not in line and line.strip().isdigit() is False and line.strip():
                # Translate the subtitle text
                src_text = line.strip()
                if src_text.strip():
                    input_ids = self.tokenizer([src_text], return_tensors="pt", padding=True, truncation=True)
                    generated_tokens = self.model.generate(**input_ids.to(self.device))
                    translated_segment = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
                    translated_lines.append(translated_segment + "\n")
                    translated_text += translated_segment.strip() + "\n"

                    # Save the translation with timestamps to CSV
                    csv_data.append([round(start_time, 2), round(end_time, 2), translated_segment.strip()])
                else:
                    translated_lines.append("\n")
            else:
                # Keep timestamp or sequence numbers unchanged
                translated_lines.append(line)

        # Write the translated SRT file
        with open(self.output_srt_file, "w", encoding="utf-8") as f:
            f.writelines(translated_lines)

        # Write the translated subtitles to CSV
        with open(self.output_csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(['start_time', 'end_time', 'Subtitles'])  # Write the header
            writer.writerows(csv_data)

        # 发送完成信号
        self.subtitlesignal.emit(translated_text.strip())
        self.signal.emit(101, 101, 101, "Translation Complete")
        print(f"[Translate] ✅ Translation completed! SRT: {self.output_srt_file}, CSV: {self.output_csv_file}")

        # 确保只发射一次 finished 信号
        self.finished.emit(True)

    def stop(self):
        self.is_stop = 1
