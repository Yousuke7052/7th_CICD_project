import os
import subprocess
import sys

# OSS相关环境变量
OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID_dev')
OSS_SECRET_ACCESS_KEY = os.getenv('OSS_SECRET_ACCESS_KEY_dev')
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT_dev')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME_dev')

def get_current_branch():
    """获取当前分支名"""
    try:
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        return branch_name.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print('Failed to get current branch: %s' % str(e))
        return None

def upload_file_to_oss(file_path, destination_path):
    """上传文件到OSS"""
    try:
        # 使用旧版字符串格式化方法
        oss_url = 'oss://%s/%s' % (OSS_BUCKET_NAME, destination_path)
        
        subprocess.run([
            'ossutil', 'cp', file_path,
            oss_url,
            '--access-key-id', OSS_ACCESS_KEY_ID,
            '--access-key-secret', OSS_SECRET_ACCESS_KEY,
            '--endpoint', OSS_ENDPOINT,
            '--force'
        ], check=True)
        print("File %s uploaded to OSS successfully." % file_path)
    except subprocess.CalledProcessError as e:
        print("Failed to upload file %s: %s" % (file_path, e))

if __name__ == '__main__':
    # 获取当前分支名
    branch_name = get_current_branch()
    
    if branch_name == 'dev':
        # 假设你要上传的是名为hello.txt的文件
        file_path = 'dev.html'  # 相对路径
        destination_path = 'dev.html'  # OSS中的目标路径
        
        # 检查文件是否存在
        if os.path.exists(file_path):
            upload_file_to_oss(file_path, destination_path)
        else:
            print("File %s does not exist." % file_path)
    else:
        print("不是dev分支提交")
        sys.exit(0)  # 结束脚本执行
