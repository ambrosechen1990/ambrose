import os
import subprocess

# 执行 Git 命令的函数
def run_git_command(command, cwd=None):
    git_path = r"C:\Program Files\Git\cmd\git.EXE"  # 指定 Git 安装路径
    try:
        # 运行 Git 命令并获取输出
        result = subprocess.run([git_path] + command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding='utf-8', cwd=cwd)  # 使用 cwd 参数指定工作目录
        print(result.stdout)  # 打印标准输出
    except subprocess.CalledProcessError as e:
        # 如果命令执行出错，打印错误信息
        print(f"错误: {e.stderr}")

# 上传文件至 GitHub 的主函数
def upload_to_github(local_folder, repo_url):
    # 检查本地文件夹是否存在
    if not os.path.isdir(local_folder):
        print(f"错误: 文件夹 {local_folder} 不存在!")
        return

    # 切换到本地项目文件夹
    run_git_command(["init"], cwd=local_folder)  # 初始化 Git 仓库

    # 检查是否已经设置了远程仓库
    try:
        run_git_command(["remote", "get-url", "origin"], cwd=local_folder)  # 获取远程仓库 URL
    except subprocess.CalledProcessError:
        # 如果没有设置远程仓库，则添加远程仓库
        run_git_command(["remote", "add", "origin", repo_url], cwd=local_folder)

    # 检查当前是否存在分支
    try:
        run_git_command(["branch"], cwd=local_folder)  # 查看本地分支
    except subprocess.CalledProcessError:
        # 如果没有分支，则创建并切换到 'main' 分支
        print("没有本地分支，创建并切换到 'main' 分支")
        run_git_command(["checkout", "-b", "main"], cwd=local_folder)  # 创建并切换到 main 分支

    # 拉取远程仓库的最新代码，以防止冲突
    try:
        run_git_command(["pull", "origin", "main", "--rebase"], cwd=local_folder)  # 拉取并合并远程的最新提交
    except subprocess.CalledProcessError:
        # 如果远程仓库不存在，则跳过此步骤
        print("远程仓库不存在，跳过拉取步骤。")

    # 添加本地更改的文件
    run_git_command(["add", "."], cwd=local_folder)  # 添加所有文件到暂存区

    # 提交更改
    run_git_command(["commit", "-m", "自动化提交"], cwd=local_folder)  # 提交文件到本地仓库

    # 推送更改到 GitHub
    run_git_command(["push", "-u", "origin", "main"], cwd=local_folder)  # 将提交推送到 GitHub

# 使用时提供本地文件夹路径和 GitHub 仓库地址
upload_to_github(r"E:\python\testcases", "https://github.com/ambrosechen1990/ambrose.git")
