import subprocess
import os

def run_git_commands():
    # 切换到当前脚本所在目录（iot）
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    try:
        # 添加所有更改
        subprocess.run(["git", "add", "."], check=True)

        # 提交更改（你也可以把提交信息做成动态的）
        subprocess.run(["git", "commit", "-m", "Auto commit: update all subfolders"], check=True)

        # 推送到远程仓库（默认使用 main 分支）
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("✅ Git push 成功")

    except subprocess.CalledProcessError as e:
        print("❌ Git 操作失败：", e)

if __name__ == "__main__":
    run_git_commands()
