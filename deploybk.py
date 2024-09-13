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
    bucket_name_env = f'OSS_BUCKET_NAME_{branch_name.upper()}'
    access_key_id_env = f'OSS_ACCESS_KEY_ID_{branch_name.upper()}'
    secret_access_key_env = f'OSS_SECRET_ACCESS_KEY_{branch_name.upper()}'
    endpoint_env = f'OSS_ENDPOINT_{branch_name.upper()}'

    bucket_name = os.getenv(bucket_name_env)
    access_key_id = os.getenv(access_key_id_env)
    secret_access_key = os.getenv(secret_access_key_env)
    endpoint = os.getenv(endpoint_env)

    log('Environment Variables:')
    log(f'  {bucket_name_env}: {bucket_name}')
    log(f'  {access_key_id_env}: {"<hidden>" if access_key_id else "Not set"}')
    log(f'  {secret_access_key_env}: {"<hidden>" if secret_access_key else "Not set"}')
    log(f'  {endpoint_env}: {endpoint}')

    return bucket_name, access_key_id, secret_access_key, endpoint

def check_for_new_commits():
    """检查是否有新的提交"""
    max_retries = 3
    delay = 5
    for attempt in range(max_retries):
        try:
            subprocess.check_call(["git", "pull"])
            # 使用 Popen 和 communicate 来捕获输出
            p = subprocess.Popen(["git", "log", "--oneline", "HEAD@{1}", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, _ = p.communicate()
            return output.strip() != b''
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:  # 如果不是最后一次尝试
                log(f'Failed to check for new commits (Attempt {attempt + 1}): {e}, Retrying in {delay} seconds...')
                time.sleep(delay)
            else:
                log(f'Failed to check for new commits after {max_retries} attempts: {e}')
                return False

def upload_file_to_oss(local_file, destination_path, bucket_name, access_key_id, secret_access_key, endpoint):
    """上传单个文件到OSS"""
    oss_url = f'oss://{bucket_name}/{destination_path}'
    try:
        log(f'Uploading file {local_file} to {oss_url}...')
        # 使用 ossutil 上传文件
        subprocess.run([
            'ossutil', 'cp', local_file,
            oss_url,
            '--access-key-id', access_key_id,
            '--access-key-secret', secret_access_key,
            '--endpoint', endpoint
        ], check=True)
        log(f'File {local_file} uploaded to OSS successfully.')
    except subprocess.CalledProcessError as e:
        log(f'Failed to upload file {local_file}: {e}')

def main():
    # 获取当前分支名
    branch_name = get_current_branch()

    if branch_name is None:
        log("Failed to determine the current branch.")
        return

    # 检查分支是否为 dev 或 prod
    if branch_name not in ['dev', 'prod']:
        log(f"Unsupported branch: {branch_name}")
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
        local_files = [
            ('/path/to/your/local/dev.html', 'dev.html')
        ]
    elif branch_name == 'prod':
        local_files = [
            ('/path/to/your/local/prod.html', 'prod.html')
        ]
    else:
        log(f"Unsupported branch: {branch_name}")
        return

    # 上传文件到OSS
    for local_file, destination_path in local_files:
        upload_file_to_oss(local_file, destination_path, bucket_name, access_key_id, secret_access_key, endpoint)

if __name__ == '__main__':
    log(f"**********Python version: {sys.version}**********")
    main()