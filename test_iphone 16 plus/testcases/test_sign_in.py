import traceback
import pytest
import time
import os
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options  # iOS 也可复用
from selenium.common import InvalidSessionIdException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 全局变量用于复用 options 配置
options = None


# ========================
# pytest hook：测试失败截图保存
# ========================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call' and report.failed:
        instance = getattr(item, 'instance', None)
        if instance:
            driver = getattr(instance, 'driver', None)
            if driver:
                filename = f"screenshots/{item.name}_{int(time.time())}.png"
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                driver.save_screenshot(filename)
                print(f"失败截图已保存：{filename}")


# ========================
# Appium driver 启动与关闭（session 级别，只执行一次）
# ========================
@pytest.fixture(scope='session')
def setup_driver():
    global options
    options = UiAutomator2Options()

    # iOS 配置项
    options.set_capability("platformName", "iOS")
    options.set_capability("platformVersion", "18.4")
    options.set_capability("deviceName", "iPhone 16 Plus")
    options.set_capability("automationName", "XCUITest")
    options.set_capability("udid", "00008140-000648C82ED0801C")
    options.set_capability("bundleId", "com.xingmai.tech")
    options.set_capability("includeSafariInWebviews", True)
    options.set_capability("newCommandTimeout", 3600)
    options.set_capability("connectHardwareKeyboard", True)

    # 创建 driver 实例，确保每次都重新创建
    driver = webdriver.Remote('http://127.0.0.1:4723', options=options)

    # 检查 driver session 是否有效
    if not driver.session_id:
        print("Session is invalid, creating new session...")
        driver.quit()
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)

    yield driver

    # 退出时检查 session 是否有效
    if driver.session_id:
        try:
            driver.quit()  # 如果会话有效，则退出
        except InvalidSessionIdException:
            print("会话已经结束，无法退出")


# ========================
# driver 注入每个测试类
# ========================
@pytest.fixture(scope='class')
def driver(request, setup_driver):
    request.cls.driver = setup_driver
    return setup_driver


# ========================
# 测试用例类
# ========================
@pytest.mark.usefixtures("driver")
class TestCase:
    # 每个测试用例前自动执行的初始化方法
    def setup_method(self, method):
        driver = self.driver
        try:
            if self.is_logged_in():
                print("检测到已登录状态，进行退出登录")
                self.logout()
                time.sleep(2)
        except:
            pass
        # 强制停止和重新启动 App
        try:
            driver.terminate_app(options.bundleId)
            time.sleep(1)
            driver.activate_app(options.bundleId)
            time.sleep(1)
        except:
            try:
                # Android 用 shell 强制停止，iOS 可跳过
                driver.execute_script("mobile: shell", {"command": "am", "args": ["force-stop", options.bundleId]})
                time.sleep(1)
                driver.activate_app(options.bundleId)
            except:
                # 最后兜底策略：重启整个 driver 会话
                driver.quit()
                driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
                self.driver = driver
                time.sleep(1)

    # 判断当前是否处于登录状态
    def is_logged_in(self):
        try:
            more_elements = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            return len(more_elements) > 0
        except:
            return False

    # 通用方法：滑动查找元素（适配 iOS 页面下滑）
    def scroll_and_find_element(self, by_locator, max_swipes=5):
        for i in range(max_swipes):
            try:
                return self.driver.find_element(*by_locator)
            except:
                size = self.driver.get_window_size()
                start_y = size['height'] * 0.7
                end_y = size['height'] * 0.3
                start_x = size['width'] * 0.5
                self.driver.swipe(start_x, start_y, start_x, end_y, duration=800)
                time.sleep(1)
        raise Exception(f"滑动{max_swipes}次后未找到元素: {by_locator}")

    # 退出登录流程（点击 mine -> 滑动找到退出区域 -> 点击 Log Out 按钮）
    def logout(self):
        try:
            print("👉 尝试点击 mine 按钮进入个人中心")
            mine_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]'))
            )
            mine_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"❌ 无法点击 mine 按钮：{e}")
            traceback.print_exc()
            return

        try:
            print("👉 滑动查找退出登录区域按钮")
            logout_cell = self.scroll_and_find_element((
                AppiumBy.XPATH, '//XCUIElementTypeTable/XCUIElementTypeCell[9]/XCUIElementTypeOther'
            ))
            logout_cell.click()
            time.sleep(1)
        except Exception as e:
            print(f"❌ 未找到退出登录区域：{e}")
            traceback.print_exc()
            return

        try:
            print("👉 等待 Log Out 确认按钮")
            confirm_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, '//XCUIElementTypeButton[@name="Log Out"]'))
            )
            confirm_button.click()
            print("✅ 成功退出登录")
            time.sleep(2)
        except Exception as e:
            print(f"❌ 点击 Log Out 确认按钮失败：{e}")
            traceback.print_exc()

    # 每个用例后自动执行，确保退出登录
    def teardown_method(self, method):
        try:
            if self.is_logged_in():
                print("🚪 Teardown：检测到已登录，退出登录")
                self.logout()
        except Exception as e:
            print("❌ Teardown异常：", e)
        finally:
            print("🛑 Driver session closed.")

    #验证APP首页登录功能按钮
    def test_signin_01(self):
        driver = self.driver
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)

            # 获取跳转后页面的标题元素
            title = self.driver.find_element(AppiumBy.XPATH,
                                             '(//XCUIElementTypeStaticText[@name="Sign In"])[1]').get_attribute('label')

            # 断言跳转是否成功
            assert title == "Sign In"
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()

    #验证登录页面到APP首页的“返回键”
    def test_signin_02(self):
        driver = self.driver
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)

            # 获取跳转后页面的标题元素
            title1 = self.driver.find_element(AppiumBy.XPATH,
                                             '(//XCUIElementTypeStaticText[@name="Sign In"])[1]').get_attribute('label')
            # 断言跳转是否成功
            assert title1 == "Sign In"
            #点击返回键，返回首页面
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="nav back"]').click()
            time.sleep(3)
            #获取跳转后页面Sign up元素
            title2 = self.driver.find_element(AppiumBy.XPATH,
                                              '//XCUIElementTypeButton[@name="Sign Up"]').get_attribute('label')
            # 断言跳转是否成功
            assert title2 == "Sign Up"
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()

    #验证正确邮箱+密码，可以登录
    def test_signin_03(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            #跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("haoc51888@gmail.com")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys("csx150128")
            time.sleep(3)
            #Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(5)
            # 获取跳转后页面home元素
            title = self.driver.find_element(AppiumBy.XPATH,'//XCUIElementTypeStaticText[@name="Home"]').get_attribute('label')
            # 断言跳转是否成功
            assert title == "Home"
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    #验证“登录”按钮，初始状态为浅色，不可点击
    def test_signin_04(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                 '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(5)
            #断言仍停留在当前页面
            title = self.driver.find_element(AppiumBy.XPATH, '//XCUIElementTypeStaticText[@name="Forgot password"]').get_attribute(
                'label')
            # 断言跳转是否成功
            assert title == "Forgot password"
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    # 验证正确账号，密码为空，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_05(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("haoc51888@gmail.com")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys(" ")# 注意：这里是空格而非空字符串
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(5)
            # 断言仍停留在当前页面
            title = self.driver.find_element(AppiumBy.XPATH,
                                             '//XCUIElementTypeStaticText[@name="Forgot password"]').get_attribute(
                'label')
            # 断言跳转是否成功
            assert title == "Forgot password"
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    #验证正确账号，密码填写错误，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_06(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                 '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
                )
            email_input.click()
            email_input.send_keys("haoc51888@gmail.com")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
                )
            password_input.clear()
            password_input.send_keys("csx150128####")
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(5)
            # 断言仍停留在当前页面”Incorrect account or password. Please check and try again.“
            title = self.driver.find_element(AppiumBy.XPATH,
                                         '//XCUIElementTypeStaticText[@name="Incorrect account or password. Please check and try again."]').get_attribute('label')
            # 断言跳转是否成功
            assert title == "Incorrect account or password. Please check and try again."
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    # 验证正确密码，账号为空，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_07(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("     ")# 注意：这里是空格而非空字符串
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys("csx150128")
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 断言仍停留在当前页面
            title = self.driver.find_element(AppiumBy.XPATH,
                                             '//XCUIElementTypeStaticText[@name="Forgot password"]').get_attribute(
                'label')
            # 断言跳转是否成功
            assert title == "Forgot password"
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    # 验证正确密码，账号其他账号-已注册账号，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_08(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("13402612115@163.com")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys("csx150128")
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 断言仍停留在当前页面”Incorrect account or password. Please check and try again.“
            title = self.driver.find_element(AppiumBy.XPATH,
                                             '//XCUIElementTypeStaticText[@name="Incorrect account or password. Please check and try again."]').get_attribute(
                'label')
            # 断言跳转是否成功
            assert title == "Incorrect account or password. Please check and try again."
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    # 验证正确密码，账号其他账号-未注册账号，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_09(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("sl021@ccdxc.com")
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys("csx150128")
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 断言仍停留在当前页面”This email is not registered. Please check and re-enter.“
            title = self.driver.find_element(AppiumBy.XPATH,
                                             '//XCUIElementTypeStaticText[@name="This email is not registered. Please check and re-enter."]').get_attribute('label')
            # 断言跳转是否成功
            assert title == "This email is not registered. Please check and re-enter."
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    # 验证清空账号的“×”按钮，可以清空账号
    def test_signin_10(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("haoc51888@gmail.com")
            # 清空账号
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="login delete"]').click()
            # 再次确认输入框为空
            cleared_email = email_input.get_attribute("value")
            assert cleared_email in ("", None), f"清除失败，当前值为: {cleared_email}"
            #输入密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys("csx150128")
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 断言仍停留在当前页面
            title = self.driver.find_element(AppiumBy.XPATH,
                                             '//XCUIElementTypeStaticText[@name="Forgot password"]').get_attribute(
                'label')
            # 断言跳转是否成功
            assert title == "Forgot password"
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    # 验证清空密码的“×”按钮，可以清空密码
    def test_signin_11(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("haoc51888@gmail.com")
            # 输入密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys("csx150128")
            # 清空密码
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="login delete"]').click()
            # 再次确认密码为空
            cleared_password = password_input.get_attribute("value")
            assert cleared_password in ("", None), f"清除失败，当前值为: {cleared_password}"
            time.sleep(3)
            # Sign In页面点击Sign按钮
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 断言仍停留在当前页面
            title = self.driver.find_element(AppiumBy.XPATH,
                                             '//XCUIElementTypeStaticText[@name="Forgot password"]').get_attribute(
                'label')
            # 断言跳转是否成功
            assert title == "Forgot password"
            print("Login successful.")
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"

    # 验证登录时，密码可以明文
    def test_signin_12(self):
        """验证APP首页登录功能按钮"""
        try:
            # 如果已登录，先退出
            more_button = self.driver.find_elements(AppiumBy.XPATH, '//XCUIElementTypeButton[@name="mine"]')
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()
                time.sleep(2)

            print("点击 Sign In 按钮")
            self.driver.implicitly_wait(3)
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="Sign In"]').click()
            time.sleep(3)
            # 跳转寻找Email和Password输入框
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeTextField"'))
            )
            email_input.click()
            email_input.send_keys("haoc51888@gmail.com")
            # 输入密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.IOS_PREDICATE, 'type == "XCUIElementTypeSecureTextField"'))
            )
            password_input.clear()
            password_input.send_keys("csx150128")
            # 点击 👁 图标，切换为明文显示
            self.driver.find_element(AppiumBy.XPATH,
                                     '//XCUIElementTypeButton[@name="login pwd hide"]').click()
            time.sleep(1)  # 给UI刷新时间
            # 重新查找 password 输入框
            password_input_visible = self.driver.find_element(
                AppiumBy.IOS_PREDICATE,
                'type == "XCUIElementTypeTextField" OR type == "XCUIElementTypeSecureTextField"')
            # 判断是否明文显示（通过 type）
            field_type = password_input_visible.get_attribute("type")
            print(f"当前输入框类型: {field_type}")
            assert field_type == "XCUIElementTypeTextField", "❌ 密码未明文显示"
        except Exception as e:
            print(f"Test failed: {e}")
            traceback.print_exc()
            assert False, f"Test failed due to: {e}"
