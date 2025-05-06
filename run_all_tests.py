import sys
import pytest

def main():
    pytest_args = sys.argv[1:]
    # 添加报告参数，如果没有指定则自动加入
    if not any(arg.startswith("--html=") for arg in pytest_args):
        pytest_args += ["--html=report.html"]
    return pytest.main(pytest_args)

if __name__ == "__main__":
    sys.exit(main())