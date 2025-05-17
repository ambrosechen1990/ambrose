import sys
import pytest

def main():
    pytest_args = sys.argv[1:]
    if not any(arg.startswith("--html=") for arg in pytest_args):
        pytest_args += [
            "--html=report.html",
            "--self-contained-html",
            "--capture=sys",
            "-v"
        ]
    return pytest.main(pytest_args)

if __name__ == "__main__":
    sys.exit(main())
