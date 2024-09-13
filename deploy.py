import os
import subprocess
import sys

def log(message):
    print(message)

# def get_current_branch():
#     """获取当前分支名"""
#     branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
#     return branch_name.decode('utf-8')

def get_current_branch():
    """获取当前分支名"""
    try:
        branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        log('Current branch: %s' % branch_name.decode('utf-8'))
        return branch_name.decode('utf-8')
    except subprocess.CalledProcessError as e:
        log('Failed to get current branch: %s' % e)
        return None

def get_environment_variables(branch_name):
    """根据分支名获取环境变量"""
    bucket_name_env = 'OSS_BUCKET_NAME_{}'.format(branch_name)
    access_key_id_env = 'OSS_ACCESS_KEY_ID_{}'.format(branch_name)
    secret_access_key_env = 'OSS_SECRET_ACCESS_KEY_{}'.format(branch_name)
    endpoint_env = 'OSS_ENDPOINT_{}'.format(branch_name)

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
    try:
        subprocess.check_call(["git", "pull"])
        # 使用Popen和communicate来捕获输出
        p = subprocess.Popen(["git", "log", "--oneline", "HEAD@{1}", "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = p.communicate()
        return output.strip() != ""
    except subprocess.CalledProcessError as e:
        log('Failed to check for new commits: %s' % e)
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
        log("Unsupported branch: %s" % branch_name)
        return

    # 上传文件到OSS
    for local_file, destination_path in local_files:
        upload_file_to_oss(local_file, destination_path, bucket_name, access_key_id, secret_access_key, endpoint)

if __name__ == '__main__':
    log("**********Python version: %s**********" % sys.version)
    main()
