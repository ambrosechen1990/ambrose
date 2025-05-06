import os
import subprocess

# 执行 Git 命令的函数
def run_git_command(command, cwd=None):
    git_path = "git"  # 在 macOS 上，直接用'git'，系统会在PATH中查找
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
    # 1. 检查本地文件夹是否存在
    if not os.path.isdir(local_folder):
        print(f"错误: 文件夹 {local_folder} 不存在！请确认路径是否正确。")
        return

    # 2. 切换到本地项目文件夹
    run_git_command(["init"], cwd=local_folder)  # 初始化Git仓库（如果已初始化会检测无害）

    # 3. 检查是否已经设置了远程仓库
    try:
        run_git_command(["remote", "get-url", "origin"], cwd=local_folder)
    except subprocess.CalledProcessError:
        # 没有设置远程，则添加
        run_git_command(["remote", "add", "origin", repo_url], cwd=local_folder)

    # 4. 检查本地分支
    try:
        run_git_command(["branch"], cwd=local_folder)
    except subprocess.CalledProcessError:
        # 如果没有任何分支，创建一个 'main' 分支
        print("没有本地分支，创建并切换到 'main' 分支")
        run_git_command(["checkout", "-b", "main"], cwd=local_folder)

    # 5. 拉取远程代码，避免冲突（如果远程不存在会出错）
    try:
        run_git_command(["pull", "origin", "main", "--rebase"], cwd=local_folder)
    except subprocess.CalledProcessError:
        print("远程仓库不存在，跳过拉取步骤。")

    # 6. 添加所有改动
    run_git_command(["add", "."], cwd=local_folder)

    # 7. 提交
    # 可以在提交前检测是否有改动，否则提交会失败
    try:
        run_git_command(["commit", "-m", "自动化提交"], cwd=local_folder)
    except subprocess.CalledProcessError:
        print("没有变化，不需要提交。")

    # 8. 推送到远程仓库
    run_git_command(["push", "-u", "origin", "main"], cwd=local_folder)

# 使用示例
local_path = "/Users/ambrose/Desktop/iot/test_Galaxy S24 Ultra"  # 你的路径
repo_url = "https://github.com/ambrosechen1990/ambrose.git"  # 你的仓库地址

# 运行前，确认路径存在
if os.path.isdir(local_path):
    upload_to_github(local_path, repo_url)
else:
    print(f"路径不存在：{local_path}，请确认路径正确！")