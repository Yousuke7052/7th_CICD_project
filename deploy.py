import os
import subprocess

def get_current_branch():
    """获取当前分支名"""
    branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()
    return branch_name

def get_environment_variables(branch_name):
    """根据分支名获取环境变量"""
    bucket_name_env = 'BUCKET_NAME_%s' % branch_name
    access_key_id_env = 'OSS_ACCESS_KEY_ID_%s' % branch_name
    secret_access_key_env = 'OSS_SECRET_ACCESS_KEY_%s' % branch_name
    endpoint_env = 'OSS_ENDPOINT_%s' % branch_name

    bucket_name = os.getenv(bucket_name_env)
    access_key_id = os.getenv(access_key_id_env)
    secret_access_key = os.getenv(secret_access_key_env)
    endpoint = os.getenv(endpoint_env)

    return bucket_name, access_key_id, secret_access_key, endpoint

def fetch_deploy_script(branch_name):
    """从main分支拉取最新的deploy.sh脚本"""
    subprocess.run(["git", "fetch", "origin", "main"])
    subprocess.run(["cp", "$(git show main:deploy.sh)", "deploy.sh.main"])
    subprocess.run(["chmod", "+x", "deploy.sh.main"])

def execute_deploy_script():
    """执行从main分支拉取的deploy.sh脚本"""
    subprocess.run(["./deploy.sh.main"])

def upload_directory_to_oss(local_dir, destination_path, bucket_name, access_key_id, secret_access_key, endpoint):
    """上传目录到OSS"""
    oss_url = 'oss://%s/%s' % (bucket_name, destination_path)
    try:
        subprocess.run([
            'ossutil', 'cp', local_dir,
            oss_url,
            '-r',  # 递归选项
            '--access-key-id', access_key_id,
            '--access-key-secret', secret_access_key,
            '--endpoint', endpoint
        ], check=True)
        print("Directory %s uploaded to OSS successfully." % local_dir)
    except subprocess.CalledProcessError as e:
        print("Failed to upload directory %s: %s" % (local_dir, e))

def main():
    # 获取当前分支名
    branch_name = get_current_branch()

    # 根据分支名确定环境变量
    bucket_name, access_key_id, secret_access_key, endpoint = get_environment_variables(branch_name)

    # 检查环境变量是否设置正确
    if not all([bucket_name, access_key_id, secret_access_key, endpoint]):
        print("Missing required environment variables.")
        return

    # 本地目录路径和目标路径
    local_dir_path = 'project_2'
    destination_path = 'project_2'

    # 从main分支拉取最新的deploy.sh脚本
    fetch_deploy_script(branch_name)

    # 执行从main分支拉取的deploy.sh脚本
    execute_deploy_script()

    # 上传目录到OSS
    upload_directory_to_oss(local_dir_path, destination_path, bucket_name, access_key_id, secret_access_key, endpoint)

if __name__ == '__main__':
    main()
