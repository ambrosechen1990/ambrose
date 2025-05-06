import os
import subprocess


# 运行git命令的基础函数
def run_git_command(command, cwd=None):
    git_executable = "git"  # 系统PATH中的git
    try:
        result = subprocess.run(
            [git_executable] + command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            cwd=cwd
        )
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"错误: {e.stderr}")
        raise


# 核心流程：初始化、设置远程、提交、推送
def push_to_github(local_dir, repo_name):
    # 1. 获取GITHUB_TOKEN环境变量
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("请先设置环境变量 GITHUB_TOKEN")
        return

    # 2. 构造带Token的远程仓库URL
    repo_url_with_token = f"https://{token}@github.com/你的用户名/{repo_name}.git"
    # 例：https://ghp_xxxxx@github.com/ambrosechen1990/ambrose.git

    # 3. 检查路径
    if not os.path.isdir(local_dir):
        print(f"路径不存在：{local_dir}")
        return

    # 4. 初始化仓库（如果已初始化不会影响）
    run_git_command(["init"], cwd=local_dir)

    # 5. 设置远程仓库（如果不存在）
    try:
        run_git_command(["remote", "get-url", "origin"], cwd=local_dir)
        print("远程仓库已存在，跳过添加。")
    except:
        print("添加远程仓库")
        run_git_command(["remote", "set-url", "origin", repo_url_with_token], cwd=local_dir)

    # 6. 添加所有文件
    run_git_command(["add", "."], cwd=local_dir)

    # 7. 提交
    try:
        run_git_command(["commit", "-m", "自动提交"], cwd=local_dir)
    except:
        print("没有新变化或提交失败，跳过.")

    # 8. 推送
    try:
        run_git_command(["push", "-u", "origin", "main"], cwd=local_dir)
        print("推送成功！")
    except Exception as e:
        print(f"推送失败：{e}")


# 使用示例
if __name__ == "__main__":
    # 你的本地路径
    local_directory = "/Users/ambrose/Desktop/iot/test_Galaxy S24 Ultra"
    # 你的仓库名（不要写完整URL，只写仓库名部分）
    repo_name = "ambrose"

    # 运行前确认环境变量已设置
    push_to_github(local_directory, repo_name)