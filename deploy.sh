#!/bin/bash

# 获取当前分支名
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)

# 设置OSS存储桶名称
if [ "$BRANCH_NAME" == "dev" ]; then
    BUCKET_NAME="dev-my-website"
elif [ "$BRANCH_NAME" == "prod" ]; then
    BUCKET_NAME="prod-my-website"
else
    echo "Unsupported branch, skipping deployment."
    exit 1
fi

# 安装阿里云CLI
pip install oss2

# 设置OSS访问密钥
export OSS_ACCESS_KEY_ID="your_access_key_id"
export OSS_ACCESS_KEY_SECRET="your_access_key_secret"

# 清除OSS存储桶中的旧文件
ossutil rm -rf oss://$BUCKET_NAME/*

# 上传文件到OSS存储桶
ossutil cp -r ./ dist/
ossutil cp -r ./ dist/ oss://$BUCKET_NAME/

echo "Deployment to $BUCKET_NAME completed successfully."
