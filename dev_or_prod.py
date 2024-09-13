def validate_branch(branch_name):
    """验证分支名是否为 dev 或 prod"""
    supported_branches = ['dev', 'prod']
    
    if branch_name in supported_branches:
        return True
    else:
        log('Unsupported branch: %s' % branch_name)
        return False

def log(message):
    print(message)

# 示例使用
if __name__ == '__main__':
    branches_to_test = ['dev', 'prod', 'master', 'feature-branch']

    for branch in branches_to_test:
        if validate_branch(branch):
            log(f'Branch "{branch}" is supported.')
        else:
            log(f'Branch "{branch}" is not supported.')
