import pytest

if __name__ == "__main__":
    pytest.main([
        ".",                        # 执行 tests 文件夹下所有 test_*.py 文件
        "--html=report.html",          # 生成测试报告
        "--self-contained-html",       # 把 CSS/JS 都内嵌进报告中
        "--capture=sys",               # 允许 print 输出显示在报告中
        "-v"                           # 显示详细信息
    ])
