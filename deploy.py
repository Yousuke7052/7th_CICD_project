import os
import subprocess
import sys
import time
import shutil

def log(message):
    print(message)

def get_current_branch():
    """获取当前分支名"""
    try:
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        return branch_name.decode('utf-8')
    except subprocess.CalledProcessError as e:
        log('Failed to get current branch: %s' % str(e))
        return None

def get_environment_variables(branch_name):
    """根据分支名获取环境变量"""
    bucket_name_env = 'OSS_BUCKET_NAME_%s' % branch_name
    access_key_id_env = 'OSS_ACCESS_KEY_ID_%s' % branch_name
    secret_access_key_env = 'OSS_SECRET_ACCESS_KEY_%s' % branch_name
    endpoint_env = 'OSS_ENDPOINT_%s' % branch_name

    bucket_name = os.getenv(bucket_name_env)
    access_key_id = os.getenv(access_key_id_env)
    secret_access_key = os.getenv(secret_access_key_env)
    endpoint = os.getenv(endpoint_env)

    log('Environment Variables:')
    log('  %s: %s' % (bucket_name_env, bucket_name))
    log('  %s: %s' % (access_key_id_env, '<hidden>' if access_key_id else 'Not set'))
    log('  %s: %s' % (secret_access_key_env, '<hidden>' if secret_access_key else 'Not set'))
    log('  %s: %s' % (endpoint_env, endpoint))

    return bucket_name, access_key_id, secret_access_key, endpoint

def check_for_new_commits():
    """检查是否有新的提交"""
    max_retries = 3
    delay = 5
    for attempt in range(max_retries):
        try:
            subprocess.check_call(["git", "pull"])
            # 使用Popen和communicate来捕获输出
            p = subprocess.Popen(["git", "log", "--oneline", "HEAD@{1}", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = p.communicate()
            return output.strip() != b''
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:  # 如果不是最后一次尝试
                log('Failed to check for new commits (Attempt %d): %s, Retrying in %d seconds...' % (attempt + 1, str(e), delay))
                time.sleep(delay)
            else:
                log('Failed to check for new commits after %d attempts: %s' % (max_retries, str(e)))
                return False

def upload_file_to_oss(file_path, destination_path, bucket_name, access_key_id, secret_access_key, endpoint):
    """上传单个文件到OSS"""
    oss_url = 'oss://%s/%s' % (bucket_name, destination_path)
    try:
        log('Uploading file %s to %s...' % (file_path, oss_url))
        # 使用ossutil上传文件
        subprocess.run([
            'ossutil', 'cp', file_path,
            oss_url,
            '--access-key-id', access_key_id,
            '--access-key-secret', secret_access_key,
            '--endpoint', endpoint
        ], check=True)
        log('File %s uploaded to OSS successfully.' % file_path)
    except subprocess.CalledProcessError as e:
        log('Failed to upload file %s: %s' % (file_path, str(e)))

def handle_file(branch_name, target_file_path, destination_path):
    """处理文件：检查文件是否存在、上传文件"""
    # 检查本地文件是否存在
    if not os.path.exists(target_file_path):
        log('File does not exist at path: %s' % target_file_path)
        return False

    # 根据分支名确定环境变量
    bucket_name, access_key_id, secret_access_key, endpoint = get_environment_variables(branch_name)

    # 检查环境变量是否设置正确
    if not all([bucket_name, access_key_id, secret_access_key, endpoint]):
        log('Missing required environment variables.')
        return False

    # 上传文件到OSS
    upload_file_to_oss(target_file_path, destination_path, bucket_name, access_key_id, secret_access_key, endpoint)
    return True

def handle_branch_logic():
    """处理与分支相关的逻辑"""
    # 获取当前分支名
    branch_name = get_current_branch()
    print("目前的分支是: %s" % branch_name)

    if branch_name is None:
        log('Failed to determine the current branch.')
        return

    # 检查分支是否为 dev 或 prod
    if branch_name not in ['dev', 'prod']:
        log('Unsupported branch: %s' % branch_name)
        return

    # 创建目标目录
    target_dir = '/path/to/your/local/'
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 复制文件到目标目录
    if branch_name == 'dev':
        original_file_path = '/root/workspace/7th_CICD_project_ewIY/dev.html'
        destination_path = 'dev.html'
    elif branch_name == 'prod':
        original_file_path = '/root/workspace/7th_CICD_project_ewIY/prod.html'
        destination_path = 'prod.html'

    target_file_path = os.path.join(target_dir, os.path.basename(original_file_path))
    shutil.copy2(original_file_path, target_file_path)

    # 检查是否有新的提交
    if not check_for_new_commits():
        log('No new commits, skipping deployment.')
        return
        
    log('==========Current working directory: %s' % os.getcwd())

    # 处理文件
    handle_file(branch_name, target_file_path, destination_path)

def main():
    """主函数"""
    log('**********Python version: %s**********' % sys.version)
    handle_branch_logic()

if __name__ == '__main__':
    # 确保当前目录为脚本所在的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
