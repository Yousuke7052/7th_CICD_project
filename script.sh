#!/bin/bash

# 输出环境变量以验证它们是否被正确设置
echo "Checking environment variables..."
env | grep OSS

# 导出环境变量
export OSS_BUCKET_NAME_DEV=${OSS_BUCKET_NAME_DEV:-""}
export OSS_ACCESS_KEY_ID_DEV=${OSS_ACCESS_KEY_ID_DEV:-""}
export OSS_SECRET_ACCESS_KEY_DEV=${OSS_SECRET_ACCESS_KEY_DEV:-""}
export OSS_ENDPOINT_DEV=${OSS_ENDPOINT_DEV:-""}

# 确保Python命令可用
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed or not in PATH."
    exit 1
fi

# 运行Python脚本
# 确保使用绝对路径或确保当前目录包含Python脚本
python3 script.py
