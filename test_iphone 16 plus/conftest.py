def pytest_addoption(parser):
    parser.addoption(
        "--click-signin",
        action="store_true",
        default=False,
        help="是否点击 Sign In 按钮"
    )

import pytest

@pytest.fixture
def should_click_sign_in(request):
    return request.config.getoption("--click-signin")
