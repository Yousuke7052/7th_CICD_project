import os
import subprocess
import sys
import time

def log(message):
    print(message)

def get_current_branch():
    """获取当前分支名"""
    try:
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        return branch_name.decode('utf-8')
    except subprocess.CalledProcessError as e:
        log('Failed to get current branch: %s' % e)
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
                log('Failed to check for new commits (Attempt %d): %s, Retrying in %d seconds...' % (attempt + 1, e, delay))
                time.sleep(delay)
            else:
                log('Failed to check for new commits after %d attempts: %s' % (max_retries, e))
                return False

def upload_file_to_oss(local_file, destination_path, bucket_name, access_key_id, secret_access_key, endpoint):
    """上传单个文件到OSS"""
    oss_url = 'oss://%s/%s' % (bucket_name, destination_path)
    try:
        log('Uploading file %s to %s...' % (local_file, oss_url))
        # 使用ossutil上传文件
        subprocess.run([
            'ossutil', 'cp', local_file,
            oss_url,
            '--access-key-id', access_key_id,
            '--access-key-secret', secret_access_key,
            '--endpoint', endpoint
        ], check=True)
        log('File %s uploaded to OSS successfully.' % local_file)
    except subprocess.CalledProcessError as e:
        log('Failed to upload file %s: %s' % (local_file, e))

def main():
    # 获取当前分支名
    branch_name = get_current_branch()

    if branch_name is None:
        log("Failed to determine the current branch.")
        return

    # 检查分支是否为 dev 或 prod
    if branch_name not in ['dev', 'prod']:
        log("Unsupported branch: %s" % branch_name)
        return

    # 检查是否有新的提交
    if not check_for_new_commits():
        log("No new commits, skipping deployment.")
        return

    # 根据分支名确定环境变量
    bucket_name, access_key_id, secret_access_key, endpoint = get_environment_variables(branch_name)

    # 检查环境变量是否设置正确
    if not all([bucket_name, access_key_id, secret_access_key, endpoint]):
        log("Missing required environment variables.")
        return

    # 明确指定本地文件路径和目标路径
    if branch_name == 'dev':
        local_file = 'dev.html'
        destination_path = 'dev.html'
    elif branch_name == 'prod':
        local_file = 'prod.html'
        destination_path = 'prod.html'
    else:
        log("Unsupported branch: %s" % branch_name)
        return

    # 检查本地文件是否存在
    if not os.path.exists(local_file):
        log("File does not exist at path: %s" % local_file)
        return

    # 上传文件到OSS
    upload_file_to_oss(local_file, destination_path, bucket_name, access_key_id, secret_access_key, endpoint)

if __name__ == '__main__':
    log("**********Python version: %s**********" % sys.version)
    main()
