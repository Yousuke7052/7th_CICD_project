import os

# 获取环境变量
bucket_name = os.getenv('OSS_BUCKET_NAME_DEV')
access_key_id = os.getenv('OSS_ACCESS_KEY_ID_DEV')
secret_access_key = os.getenv('OSS_SECRET_ACCESS_KEY_DEV')
endpoint = os.getenv('OSS_ENDPOINT_DEV')

# 输出环境变量以验证它们是否被正确读取
print("OSS_BUCKET_NAME_DEV: {}".format(bucket_name))
print("OSS_ACCESS_KEY_ID_DEV: {}".format('<hidden>' if access_key_id else 'Not set'))
print("OSS_SECRET_ACCESS_KEY_DEV: {}".format('<hidden>' if secret_access_key else 'Not set'))
print("OSS_ENDPOINT_DEV: {}".format(endpoint))

# 检查环境变量是否设置正确
if not all([bucket_name, access_key_id, secret_access_key, endpoint]):
    raise ValueError("One or more required environment variables are missing.")

print("All required environment variables are set correctly.")
