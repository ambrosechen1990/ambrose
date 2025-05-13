import subprocess
import sys
from datetime import datetime


# 运行 Git 命令的通用函数
def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ 成功: {' '.join(command)}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败： {e}")
        if e.stderr:
            print(e.stderr)
        return False


# 合并冲突解决
def resolve_merge_conflicts(cwd=None):
    print("开始解决合并冲突...")

    # 解决 .DS_Store 文件的冲突（如果有）
    run_command(['git', 'rm', '.DS_Store'], cwd=cwd)

    # 你可以根据需要添加更多需要处理的文件，例如删除不必要的文件或自动处理特定文件
    print("冲突文件处理完成！")


def main():
    commit_message = f"Auto commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    # 切换到脚本所在目录（确保是在项目根目录下）
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Git 操作流程
    if not run_command(['git', 'add', '.']):
        sys.exit(1)

    if not run_command(['git', 'commit', '-m', commit_message]):
        print("⚠️ 没有改动可提交")

    if not run_command(['git', 'push', 'origin', 'main']):
        # 如果 push 失败（例如合并冲突），尝试解决冲突并重新推送
        resolve_merge_conflicts(script_dir)
        if not run_command(['git', 'push', 'origin', 'main']):
            sys.exit(1)


if __name__ == "__main__":
    main()
