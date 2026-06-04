#!/bin/bash

# PyCinemetricsV2 启动脚本
# 用于在 App 内部设置必要的环境变量

# 获取应用程序所在目录
APP_DIR="$(cd "$(dirname "$0")" && pwd)"

# 设置环境变量（防止多线程冲突）
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# 运行主程序
exec "$APP_DIR/pyCinemetricsV2" "$@"
