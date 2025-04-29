import pytest
import traceback
from appium import webdriver
from appium.options.android import UiAutomator2Options

@pytest.fixture(scope="module")
def driver():
    options = UiAutomator2Options()
    # 使用 appium: 前缀设置能力项
    options.set_capability('appium:platformName', 'Android')
    options.set_capability('appium:platformVersion', '14')
    options.set_capability('appium:deviceName', 'Galaxy S24 Ultra')
    options.set_capability('appium:appPackage', 'com.xingmai.tech')
    options.set_capability('appium:appActivity', 'com.xingmai.splash.SplashActivity')
    options.set_capability('appium:noReset', True)
    options.set_capability('appium:automationName', 'UiAutomator2')
    options.set_capability('appium:fullContextList', True)

    try:
        driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)
        yield driver
        driver.quit()
    except Exception as e:
        print(f'❌ Appium driver 启动失败: {str(e)}')
        traceback.print_exc()
        pytest.fail('Appium driver failed to start')