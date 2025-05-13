import subprocess
import sys
from datetime import datetime
import os

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ 成功: {' '.join(command)}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 操作失败： {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def main():
    commit_message = f"Auto commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 添加改动
    if not run_command(['git', 'add', '.']):
        sys.exit(1)

    # 提交改动（没有变更也不会中断）
    run_command(['git', 'commit', '-m', commit_message])

    # 拉取远程（使用 rebase 保持提交线性）
    if not run_command(['git', 'pull', 'origin', 'main', '--rebase']):
        print("⚠️ Git pull --rebase 失败，请手动检查冲突")
        sys.exit(1)

    # 推送改动
    if not run_command(['git', 'push', 'origin', 'main']):
        print("❌ 推送失败，可尝试手动执行: git push origin main --force （慎用）")
        sys.exit(1)

if __name__ == "__main__":
    main()
