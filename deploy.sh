#!/bin/bash

# 从main分支拉取最新的deploy.sh脚本
git fetch origin main:main
cp $(git show main:deploy.sh) deploy.sh

# 给予脚本执行权限
chmod +x deploy.sh

# 获取当前分支名
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# 设置OSS存储桶名称
BUCKET_NAME="${BUCKET_NAME_${BRANCH_NAME}}"
OSS_ACCESS_KEY_ID="${OSS_ACCESS_KEY_ID_${BRANCH_NAME}}"
OSS_ACCESS_KEY_SECRET="${OSS_ACCESS_KEY_SECRET_${BRANCH_NAME}}"
HTML_FILE="${HTML_FILE}_${BRANCH_NAME}"

# 检查环境变量是否设置正确
if [[ -z "$BUCKET_NAME" || -z "$OSS_ACCESS_KEY_ID" || -z "$OSS_ACCESS_KEY_SECRET" || -z "$HTML_FILE" ]]; then
    echo "Missing required environment variables."
    exit 1
fi

# 设置OSS访问密钥
export OSS_ACCESS_KEY_ID="$OSS_ACCESS_KEY_ID"
export OSS_ACCESS_KEY_SECRET="$OSS_ACCESS_KEY_SECRET"

# 清除OSS存储桶中的旧文件
ossutil rm -rf oss://$BUCKET_NAME/*

# 上传文件到OSS存储桶
ossutil cp $HTML_FILE oss://$BUCKET_NAME/

echo "Deployment to $BUCKET_NAME completed successfully."
