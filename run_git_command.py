import os
import subprocess

# 运行git命令的函数
def run_git_command(command, cwd=None):
    git_path = "git"  # 假设在系统PATH中
    try:
        result = subprocess.run(
            [git_path] + command, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', cwd=cwd
        )
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"错误: {e.stderr}")
        raise e

# 主要上传流程
def upload_to_github(local_folder, repo_url_with_token):
    # 1. 确认路径是否存在
    if not os.path.isdir(local_folder):
        print(f"错误: 文件夹 {local_folder} 不存在！")
        return

    # 2. 初始化仓库（若已初始化，影响不大）
    run_git_command(["init"], cwd=local_folder)

    # 3. 检查远程仓库
    try:
        run_git_command(["remote", "get-url", "origin"], cwd=local_folder)
        print("已存在远程仓库，跳过添加远程步骤。")
    except:
        # 这里用带Token的URL设置远程
        run_git_command(["remote", "set-url", "origin", repo_url_with_token], cwd=local_folder)

    # 4. 添加所有变更文件
    run_git_command(["add", "."], cwd=local_folder)

    # 5. 提交
    try:
        run_git_command(["commit", "-m", "自动化提交"], cwd=local_folder)
    except:
        print("没有新变化或提交失败（可能无变化），跳过此步。")
        pass

    # 6. 推送到远程
    try:
        run_git_command(["push", "-u", "origin", "main"], cwd=local_folder)
        print("推送成功！")
    except Exception as e:
        print(f"推送失败！请确认远程仓库正确，且有权限。详细错误：{e}")

# 你的本地路径和仓库地址
local_path = "/Users/ambrose/Desktop/iot/test_Galaxy S24 Ultra"
# 用你自己生成的Token替换下面的示例Token
TOKEN = "ghp_YOURACTUALTOKEN1234567890"
REPO_URL = f"https://{TOKEN}@github.com/ambrosechen1990/ambrose.git"

# 判断路径是否存在与执行上传
if os.path.isdir(local_path):
    upload_to_github(local_path, REPO_URL)
else:
    print(f"路径不存在：{local_path}，请确认路径是否正确！")