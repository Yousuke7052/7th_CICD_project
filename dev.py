import os
import subprocess
import sys

# OSS相关环境变量
OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID_dev')
OSS_SECRET_ACCESS_KEY = os.getenv('OSS_SECRET_ACCESS_KEY_dev')
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT_dev')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME_dev')

def get_current_branch():
    """嘗試获取当前分支名"""
    try:
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        return branch_name.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print('Failed to get current branch / 嘗試獲取dev分支失敗了: %s' % str(e))
        return None

def check_file_changed(file_path):
    """检查特定文件是否在最近的提交中有更改"""
    try:
        last_commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD~1']).strip().decode('utf-8')
        current_commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip().decode('utf-8')
        diff_output = subprocess.check_output(['git', 'diff', '--name-only', last_commit_hash, current_commit_hash, file_path])
        return bool(diff_output.strip())
    except subprocess.CalledProcessError as e:
        print('Failed to check file changes / dev分支本次無提交oss靜態網站更新需求: %s' % str(e))
        return False

def upload_file_to_oss(file_path, destination_path):
    """上传文件到OSS"""
    try:
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
        file_path = 'dev.html'  # DevOps中會在同級目錄下
        destination_path = 'dev.html'  # OSS中的暫定目標路徑
        
        # 检查文件是否更新過
        if check_file_changed(file_path):
            # 上傳更新的文件至oss
            upload_file_to_oss(file_path, destination_path)
        else:
            print("File %s does not exist. / %s 未檢測到更新" % (file_path,file_path))
    else:
        print("當前提交的分支是 %s ，但沒有更新的代碼" % branch_name)
        sys.exit(0)  # 结束脚本执行
