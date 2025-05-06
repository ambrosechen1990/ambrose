import os
import subprocess

# 执行 Git 命令的函数
def run_git_command(command, cwd=None):
    git_path = "git"  # 使用系统PATH中的git
    try:
        result = subprocess.run([git_path] + command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding='utf-8', cwd=cwd)
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"错误: {e.stderr}")
        raise e

# 上传到GitHub的主要流程
def upload_to_github(local_folder, repo_url):
    # 检查路径是否存在
    if not os.path.isdir(local_folder):
        print(f"错误: 文件夹 {local_folder} 不存在！请确认路径是否正确。")
        return

    # 初始化仓库
    run_git_command(["init"], cwd=local_folder)

    # 检查是否已设置远程仓库（只在未设置时添加）
    try:
        run_git_command(["remote", "get-url", "origin"], cwd=local_folder)
        print("已存在远程仓库，跳过添加远程步骤。")
    except:
        print("没有找到远程仓库，添加远程：", repo_url)
        run_git_command(["remote", "add", "origin", repo_url], cwd=local_folder)

    # 设置全局用户信息（建议只做一次，或者在全局配置中设置好）
    # run_git_command(["config", "--global", "user.name", "你的名字"])
    # run_git_command(["config", "--global", "user.email", "你的邮箱"])

    # 添加文件
    run_git_command(["add", "."], cwd=local_folder)

    # 提交（如果没有改动会出错，可捕获异常）
    try:
        run_git_command(["commit", "-m", "自动化提交"], cwd=local_folder)
    except:
        print("没有新变化或提交失败（可能无变化），跳过此步。")
        pass

    # 推送到远程仓库
    try:
        run_git_command(["push", "-u", "origin", "main"], cwd=local_folder)
        print("推送成功！")
    except Exception as e:
        print(f"推送失败！请确认远程仓库正确，且有权限。错误信息：{e}")

# 具体使用示例
local_path = "/Users/ambrose/Desktop/iot/test_Galaxy S24 Ultra"  # 你的本地路径
repo_url = "https://github.com/ambrosechen1990/ambrose.git"  # 你的GitHub仓库地址

# 确认路径存在
if os.path.isdir(local_path):
    upload_to_github(local_path, repo_url)
else:
    print(f"路径不存在：{local_path}，请确认路径是否正确！")