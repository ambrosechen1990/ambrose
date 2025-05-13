import functools
import os

import pytest


def auto_screenshot_on_failure(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            # 失败截图
            filename = f"screenshots/{self.__class__.__name__}_{int(time.time())}.png"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.driver.save_screenshot(filename)
            print(f"出错，已保存截图：{filename}")
            pytest.fail(f"测试失败，原因：{e}")
    return wrapper