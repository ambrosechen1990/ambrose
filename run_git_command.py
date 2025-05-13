import subprocess
import sys
from datetime import datetime


def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ 成功: {' '.join(command)}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败： {e}")
        print(e.stderr)
        return False


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
        sys.exit(1)


if __name__ == "__main__":
    main()
