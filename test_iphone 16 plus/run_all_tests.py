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

import pytest

if __name__ == "__main__":
    pytest.main([
        ".",                        # 执行 tests 文件夹下所有 test_*.py 文件
        "--html=report.html",          # 生成测试报告
        "--self-contained-html",       # 把 CSS/JS 都内嵌进报告中
        "--capture=sys",               # 允许 print 输出显示在报告中
        "-v"                           # 显示详细信息
    ])

