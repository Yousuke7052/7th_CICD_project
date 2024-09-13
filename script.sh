#!/bin/bash

# 输出环境变量以验证它们是否被正确设置
echo "Checking environment variables..."
env | grep OSS

# 确保Python命令可用
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed or not in PATH."
    exit 1
fi

# 运行Python脚本
python3 script.py
