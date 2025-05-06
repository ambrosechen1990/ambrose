import os
import subprocess

def run_git_command(command, cwd=None):
    git_executable = "git"
    try:
        result = subprocess.run([git_executable] + command, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding='utf-8', cwd=cwd)
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"错误: {e.stderr}")
        raise

def push_to_github(local_dir, username, repo_name):
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("请先设置环境变量 GITHUB_TOKEN")
        return

    # 构建带Token的远程地址
    repo_url = f"https://{token}@github.com/{username}/{repo_name}.git"

    # 确认路径存在
    if not os.path.isdir(local_dir):
        print(f"路径不存在：{local_dir}")
        return

    # 初始化仓库（如果已初始化，则影响不大）
    run_git_command(["init"], cwd=local_dir)

    # 设置远程仓库（如果不存在）
    try:
        run_git_command(["remote", "get-url", "origin"], cwd=local_dir)
        print("远程已存在，跳过添加。")
    except:
        run_git_command(["remote", "set-url", "origin", repo_url], cwd=local_dir)

    # 添加所有文件
    run_git_command(["add", "."], cwd=local_dir)

    # 提交
    try:
        run_git_command(["commit", "-m", "自动提交"], cwd=local_dir)
    except:
        print("没有变化，跳过提交。")

    # 推送
    try:
        run_git_command(["push", "-u", "origin", "main"], cwd=local_dir)
        print("推送成功！")
    except Exception as e:
        print(f"推送失败：{e}")

if __name__ == "__main__":
    local_dir = "/Users/ambrose/Desktop/iot/test_Galaxy S24 Ultra"  # 你的本地路径
    username = "ambrosechen1990"
    repo_name = "ambrose"
    # 先确保环境变量设置：export GITHUB_TOKEN=github_pat_...
    # 然后运行
    if os.path.isdir(local_dir):
        push_to_github(local_dir, username, repo_name)
    else:
        print(f"路径不存在：{local_dir}")