import os
import subprocess


def run_git_command(command, cwd=None):
    """执行git命令的函数"""
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"错误: {e.stderr}")
        raise


def commit_local_changes(local_dir):
    """提交本地更改以避免合并冲突"""
    try:
        # 添加所有更改
        run_git_command(["git", "add", "."], cwd=local_dir)

        # 检查是否有任何更改被暂存
        result = subprocess.run(
            ["git", "diff", "--cached", "--exit-code"],
            cwd=local_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 如果 git diff 返回代码为 0，说明没有变化
        if result.returncode == 0:
            print("没有未提交的更改。")
            return

        # 有变化则提交
        run_git_command(["git", "commit", "-m", "临时保存未提交的更改"], cwd=local_dir)

    except subprocess.CalledProcessError as e:
        print(f"提交错误：{e.stderr}")
        raise


def pull_and_push_to_github(local_dir, user_name, repo_name):
    """配置远程，拉取，提交，推送流程"""
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("请先设置环境变量 GITHUB_TOKEN")
        return

    # 构建带Token的远程URL
    remote_url = f"https://{token}@github.com/{user_name}/{repo_name}.git"

    # 检查路径
    if not os.path.isdir(local_dir):
        print(f"路径不存在：{local_dir}")
        return

    # 初始化仓库（如果已初始化无影响）
    run_git_command(["git", "init"], cwd=local_dir)

    # 确认远程仓库设置
    try:
        run_git_command(["git", "remote", "get-url", "origin"], cwd=local_dir)
        print("远程已存在，跳过添加。")
    except:
        run_git_command(["git", "remote", "set-url", "origin", remote_url], cwd=local_dir)

    # 提交本地未提交更改
    try:
        commit_local_changes(local_dir)
    except Exception as e:
        print(f"提交本地更改失败：{e}")
        return

    # 拉取远程更改以确保同步
    try:
        run_git_command(["git", "pull", "origin", "main", "--allow-unrelated-histories"], cwd=local_dir)
        print("成功拉取远程更新。")
    except Exception as e:
        print(f"拉取失败：{e}")
        return

    # 推送更改
    try:
        run_git_command(["git", "push", "-u", "origin", "main"], cwd=local_dir)
        print("推送成功！")
    except Exception as e:
        print(f"推送失败：{e}")


# 使用示例
if __name__ == "__main__":
    local_dir = "/Users/ambrose/Desktop/iot/test_Galaxy S24 Ultra"  # 你的本地路径
    user_name = "ambrosechen1990"
    repo_name = "ambrose"
    if os.path.isdir(local_dir):
        pull_and_push_to_github(local_dir, user_name, repo_name)
    else:
        print(f"路径不存在：{local_dir}")