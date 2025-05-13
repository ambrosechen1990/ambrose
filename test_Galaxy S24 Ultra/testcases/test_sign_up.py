import constant
import pytest
import time
import traceback
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import functools
import os

# 全局变量保存options配置
options = None

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call' and report.failed:
        instance = getattr(item, 'instance', None)
        if instance:
            driver = getattr(instance, 'driver', None)
            if driver:
                # 定义文件名，包含测试用例名称和时间戳
                filename = f"screenshots/{item.name}_{int(time.time())}.png"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                driver.save_screenshot(filename)
                print(f"失败截图已保存：{filename}")


@pytest.fixture(scope='session')
def setup_driver():
    # 全局配置 options
    global options
    options = UiAutomator2Options()
    options.platformName = "Android"
    options.platform_version = "14"
    options.device_name = "Galaxy S24 Ultra"
    options.app_package = "com.xingmai.tech"
    options.app_activity = "com.xingmai.splash.SplashActivity"
    options.no_reset = True
    options.automation_name = "UiAutomator2"
    options.full_context_list = True

    # 创建 driver 实例
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)

    # 传递 driver 到测试类
    yield driver
    # 测试结束后退出
    driver.quit()

@pytest.fixture(scope='class')
def driver(request, setup_driver):
    # 将 driver 分配给测试类
    request.cls.driver = setup_driver
    return setup_driver


@pytest.mark.usefixtures("driver")
class TestCase:
    def setup_method(self, method):
        # 每个测试用例前，强制退出登录，杀掉app，确保干净环境
        driver = self.driver
        # 先检测是否已登录，若登录，则退出登录
        try:
            if self.is_logged_in():
                print("检测到已登录状态，进行退出登录")
                self.logout()
                time.sleep(2)
        except:
            pass
        # 强制停止app，确保干净状态
        try:
            driver.terminate_app(options.app_package)
            time.sleep(1)
            driver.activate_app(options.app_package)
            time.sleep(1)
        except:
            # 如果terminate_app或activate_app失败，试用shell命令
            try:
                driver.execute_script("mobile: shell", {"command": "am", "args": ["force-stop", options.app_package]})
                time.sleep(1)
                driver.activate_app(options.app_package)
            except:
                # 最后手动退出会话（慎用）
                driver.quit()
                # 重新创建 driver
                driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
                self.driver = driver
                time.sleep(1)

    def is_logged_in(self):
        # 判断是否已登录：检测“More”按钮是否存在
        try:
            more_elements = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            return len(more_elements) > 0
        except:
            return False

    def logout(self):
        # 退出登录的操作
        try:
            more_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.view.View[@content-desc='More']"))
            )
            more_button.click()
            time.sleep(2)

            logout_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.view.View[12]"))
            )
            logout_button.click()
            time.sleep(1)

            confirm_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Confirm']"))
            )
            confirm_button.click()
            print("✅ 退出登录成功")
            time.sleep(2)
        except:
            print("⚠️ 退出登录异常或已退出")

    def teardown_method(self, method):
        # 测试用例后，确保退出登录
        try:
            if self.is_logged_in():
                print("🚪 Teardown：检测到已登录，退出登录")
                self.logout()
        except Exception as e:
            print("❌ Teardown异常：", e)
        finally:
            print("🛑 Driver session closed.")

    #验证输入用户名名字超过50个字符，点击“Submit”按钮
    def test_signup_01(self):
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            print("点击Sign In按钮")
            # 设置隐式等待，最多等 3 秒

            self.driver.implicitly_wait(3)
            #进入APP，查找Sign up
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[2]").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            #点击隐私政策和用户协议
            self.driver.find_element(AppiumBy.XPATH,
                                 "//android.widget.CheckBox").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)

            # 输入邮箱名称
            self.driver.find_element(AppiumBy.XPATH,
                                 "//android.widget.EditText").send_keys(constant.ran1 + "@gmail.com")
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            #点击Next按钮
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[2]").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)

            #Set Password页面设置密码
            self.driver.find_element(AppiumBy.XPATH,
                                     "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.widget.EditText[1]").send_keys("csx150128")
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.widget.EditText[2]").send_keys("csx150128")
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)

            #Set Password页面点击Next
            self.driver.find_element(AppiumBy.XPATH,
                                     "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[1]").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)

            #输入username
            self.driver.find_element(AppiumBy.XPATH,
                                     "//android.widget.EditText").send_keys(constant.ran2)
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            # 点击Submit
            self.driver.find_element(AppiumBy.XPATH,
                                     "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[2]").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)

            wait = WebDriverWait(self.driver, 10)
            # 获取“登录成功后，显示用户名”的元素
            displayed_username_element = wait.until(
                EC.presence_of_element_located(
                    (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("")')
                )
            )
            displayed_username = displayed_username_element.get_attribute("text")
            print(f"显示的用户名：{displayed_username}")

            # 获取“输入框”的内容
            input_username_element = self.driver.find_element(AppiumBy.XPATH, "//android.widget.EditText")
            input_username = input_username_element.get_attribute("text")
            print(f"输入的用户名：{input_username}")

            # 比较两个内容
            if displayed_username == input_username:
                print("用户名一致，测试通过！")
            else:
                raise AssertionError(f"用户名不一致！登录后显示：'{displayed_username}', 输入的是：'{input_username}'")
        except Exception as e:
            pytest.fail(f"元素查找失败：{e}")
            traceback.print_exc()


