import subprocess

def run_git_command(command):
    git_path = r"C:\Program Files\Git\cmd\git.EXE"  # 指定 Git 的完整路径
    try:
        result = subprocess.run([git_path] + command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")

def upload_to_github(local_folder, repo_url):
    # 初始化 Git 仓库
    run_git_command(["init"])

    # 添加远程仓库
    run_git_command(["remote", "add", "origin", repo_url])

    # 添加文件到 Git 索引
    run_git_command(["add", "."])

    # 提交文件
    run_git_command(["commit", "-m", "Initial commit"])

    # 推送到 GitHub，改为使用 main 分支
    run_git_command(["push", "-u", "origin", "main"])

# 使用时传入本地文件夹和 GitHub 仓库地址
upload_to_github("your-local-folder-path", "https://github.com/ambrosechen1990/ambrose.git")
