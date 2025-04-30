import pytest
import time
import traceback
import git
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 定义一个 Pytest 的 fixture，用于初始化和关闭 Appium driver，作用域为 class
@pytest.fixture(scope="class")
def driver(request):
    # 设置 Appium 的配置参数
    options = UiAutomator2Options()
    options.platformName = "Android"  # 指定平台名称
    options.platform_version = "14"  # 指定 Android 系统版本
    options.device_name = "Galaxy S24 Ultra"  # 指定设备名称
    options.app_package = "com.xingmai.tech"  # 应用包名
    options.app_activity = "com.xingmai.splash.SplashActivity"  # 启动入口 Activity
    options.no_reset = True  # 启动 app 时不重置应用状态
    options.automation_name = "UiAutomator2"  # 指定使用的自动化框架
    options.full_context_list = True  # 获取所有上下文（用于混合应用 H5/原生）

    print('driver连接appium服务器,并打开app')
    # 创建并连接到 Appium Server，返回 driver 实例
    driver_instance = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)

    # 将 driver 实例注入到测试类中（赋值给 self.driver）
    request.cls.driver = driver_instance

    # yield 语句之前的代码在测试开始前执行，之后的在测试结束后执行（如关闭 driver）
    yield
    driver_instance.quit()

# 使用上面的 fixture 注入 driver 到测试类中
@pytest.mark.usefixtures("driver")
class TestCase:

    def teardown_method(self):
        """用例后执行退出（如果在已登录状态）"""
        try:
            # 如果在登录后页面，尝试点击“More” → “Logout”
            more = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more:
                print("🚪 Detected login state, preparing to logout...")
                self.logout()
        except Exception as e:
            print("❌ Logout skipped or failed.")
            traceback.print_exc()

    def logout(self):
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
            print("✅ Logout successful.")
            time.sleep(2)
        except Exception as logout_e:
            print(f"⚠️ Logout failed: {logout_e}")
            traceback.print_exc()

    # 验证APP首页登录功能按钮
    def test_signin_01(self):
        """验证APP首页登录功能按钮"""
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
            # 查找并点击首页中的 “Sign In” 按钮（使用 XPath 定位）
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            # 查找跳转后页面的标题“Sign In”文本元素，获取其 text 属性
            title = self.driver.find_element(AppiumBy.XPATH,
                                         '(//android.widget.TextView[@text="Sign In"])[2]').get_attribute('text')
            # 断言标题为 “Sign In”，判断是否成功跳转到登录页面
            assert title == "Sign In"
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()

    #验证登录页面到APP首页的“返回键”
    def test_signin_02(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete

            print("Sign In back")
            # 设置隐式等待，最多等 3 秒
            self.driver.implicitly_wait(3)
            # 查找Sign In页中的 “Back” 按钮（使用 XPath 定位）
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View/android.view.View").click()
            # 等待 3 秒确保跳转页面加载完成
            # 查找跳转后页面的标题“Sign In”文本元素，获取其 text 属性
            title1 = self.driver.find_element(AppiumBy.XPATH,
                                         '//android.widget.TextView[@text="Sign In"]').get_attribute('text')
            # 查找跳转后页面的标题“Sign up”文本元素，获取其 text 属性
            title2 = self.driver.find_element(AppiumBy.XPATH,
                                         '//android.widget.TextView[@text="Sign Up"]').get_attribute('text')
            time.sleep(3)
            # 判断是否进入主页面
            assert title1 == "Sign In" and title2 == "Sign Up"
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()

    #验证正确邮箱+密码，可以登录
    def test_signin_03(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete

            print("▶️ test_signin_05 - Sign In then Logout")
            # 设置隐式等待，最多等 3 秒
            self.driver.implicitly_wait(3)

            # 查找并点击首页中的 “Sign In” 按钮（使用 XPath 定位）
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            #跳转寻找Email和Password输入框

            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc51888@gmail.com")

            password_input = WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")

            #Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(5)

            # 查找跳转后页面"home"文本元素，，获取其 text 属性
            title = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Home")'
            ).get_attribute("text")
            assert title == "Home"
            print("✅ Login successful.")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()


    #验证“登录”页面，不输入email和password,Sign In按钮无法点击
    def test_signin_04(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            print("Sign In Success")
            # 设置隐式等待，最多等 3 秒
            self.driver.implicitly_wait(3)
            # 查找并点击首页中的 “Sign In” 按钮（使用 XPath 定位）
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            #进入Sign In页面，点击Sign In按钮（使用 XPath 定位）
            self.driver.find_element(AppiumBy.XPATH,
                                 "//android.widget.ScrollView/android.view.View").click()
            # 等待 3 秒确保跳转页面加载完成
            time.sleep(3)
            #未输入Email和Password，APP仍停留在Sign In页面,查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                                         '//android.widget.TextView[@text="Incorrect account or password. Please check and try again."]').get_attribute('text')
            time.sleep(3)
            #判断是否停留在Sign In页面
            assert title == "Incorrect account or password. Please check and try again."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()


    #验证正确账号，密码为空，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_05(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
            ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc51888@gmail.com")

            password_input = WebDriverWait(self.driver,10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys(" ")# 注意：这里是空格而非空字符串

            # Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(3)

            # 未输入Email和Password，APP仍停留在Sign In页面,查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                                         '//android.widget.TextView[@text="Incorrect account or password. Please check and try again."]').get_attribute(
                'text')
            time.sleep(3)
            # 判断是否停留在Sign In页面
            assert title == "Incorrect account or password. Please check and try again."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()


    #验证正确账号，密码填写错误，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_06(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
            ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc51888@gmail.com")
            #输入错误密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("ASDFQWER !@#$%^&*()_+")
            # Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(3)

            # 未输入Email和Password，APP仍停留在Sign In页面,查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                                         '//android.widget.TextView[@text="Incorrect account or password. Please check and try again."]').get_attribute(
                'text')
            time.sleep(3)
            # 判断是否停留在Sign In页面
            assert title == "Incorrect account or password. Please check and try again."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()

    # 验证正确密码，账号为空，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_07(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                            "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
                            ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys(" ")# 注意：这里是空格而非空字符串
            time.sleep(1)
            # 输入正确密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")
            time.sleep(1)
            # Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(3)

            # 未输入Email和Password，APP仍停留在Sign In页面,查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                    '//android.widget.TextView[@text="Incorrect account or password. Please check and try again."]').get_attribute('text')
            time.sleep(3)
            # 判断是否停留在Sign In页面
            assert title == "Incorrect account or password. Please check and try again."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()


    # 验证正确密码，账号其他账号，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_08(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                            "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
                            ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("a13402612115@163.com")
            # 输入错误密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")  # 注意：这里是空格而非空字符串
            # Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(3)

            # 未输入Email和Password，APP仍停留在Sign In页面,查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                    '//android.widget.TextView[@text="Incorrect account or password. Please check and try again."]').get_attribute('text')
            time.sleep(3)
            # 判断是否停留在Sign In页面
            assert title == "Incorrect account or password. Please check and try again."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()



    #验证正确密码，账号填写错误，无法登录，提示“账号或密码错误，请确认后重试。”
    def test_signin_09(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                            "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
                            ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc1001@gmail.com")
            time.sleep(1)
             # 输入正确密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")
            time.sleep(1)
            # Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(3)

            # 查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                    '//android.widget.TextView[@text="This email is not registered. Please check and re-enter."]').get_attribute('text')
            time.sleep(3)
            # 判断是否停留在Sign In页面
            assert title == "This email is not registered. Please check and re-enter."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()


    #验证清空账号的“×”按钮，可以清空账号
    def test_signin_10(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
                                 ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc51888@gmail.com")
            time.sleep(3)
            #查找并点击email输入框×按钮，清空账号
            self.driver.find_element(AppiumBy.XPATH,
                                 '(//android.widget.ImageView[@content-desc="清除"])[1]'
                                 ).click()
            time.sleep(3)
            # 输入正确密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")
            # Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(3)

            # 未输入Email和Password，APP仍停留在Sign In页面,查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                                         '//android.widget.TextView[@text="Incorrect account or password. Please check and try again."]').get_attribute(
                'text')
            time.sleep(3)
            # 判断是否停留在Sign In页面
            assert title == "Incorrect account or password. Please check and try again."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()


    # 验证清空密码的“×”按钮，可以清空密码
    def test_signin_11(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
                                 ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc51888@gmail.com")
            time.sleep(3)
            # 输入正确密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")
            time.sleep(3)
            # 查找并点击password输入框×按钮，清空账号
            self.driver.find_element(AppiumBy.XPATH,
                                 '(//android.widget.ImageView[@content-desc="清除"])[2]'
                                 ).click()
            time.sleep(3)
            # Sign In页面点击Sign按钮
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
            )
            sign_in_button.click()
            time.sleep(3)

            # 未输入Email和Password，APP仍停留在Sign In页面,查找Incorrect account or password. Please check and try again.元素
            title = self.driver.find_element(AppiumBy.XPATH,
                                         '//android.widget.TextView[@text="Incorrect account or password. Please check and try again."]').get_attribute(
                'text')
            time.sleep(3)
            # 判断是否停留在Sign In页面
            assert title == "Incorrect account or password. Please check and try again."
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()


    #验证登录时，密码可以明文
    def test_signin_12(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete
            self.driver.implicitly_wait(3)
            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
                                 ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc51888@gmail.com")
            time.sleep(3)
            # 输入正确密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")
            time.sleep(3)
            self.driver.find_element(AppiumBy.XPATH,
                                 '//android.widget.ImageView[@content-desc="lock"]').click()
            time.sleep(3)

            # 断言密码明文显示
            assert password_input.get_attribute("password") == 'false'  # 表示明文显示
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()

    #验证登录时，密码明文后，可以再次隐藏
    def test_signin_13(self):
        """验证APP首页登录功能按钮"""
        try:
            # Check if already logged in
            more_button = self.driver.find_elements(AppiumBy.XPATH, "//android.view.View[@content-desc='More']")
            if more_button:
                print("🚪 Already logged in, logging out first...")
                self.teardown_method()  # Log out if already logged in
                time.sleep(2)  # Wait for logout to complete

            # 查找并点击首页的“Sign In”按钮，进入登录页面
            self.driver.find_element(AppiumBy.XPATH,
                                 "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[1]"
                                 ).click()
            time.sleep(3)
            # 等待并查找Email输入框可点击
            email_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
            )
            email_input.send_keys("haoc51888@gmail.com")
            time.sleep(3)
            # 输入正确密码
            password_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
            )
            password_input.send_keys("csx150128")
            time.sleep(3)

            # 第一次点击 -> 明文
            self.driver.find_element(AppiumBy.XPATH,
                                 '//android.widget.ImageView[@content-desc="lock"]').click()
            time.sleep(3)

            # 断言密码明文显示
            assert password_input.get_attribute("password") == 'false'  # 表示明文显示
            time.sleep(3)

            # 第二次点击 -> 隐藏
            self.driver.find_element(AppiumBy.XPATH,
                                 '//android.widget.ImageView[@content-desc="lock"]').click()
            time.sleep(3)

            # 断言密码隐藏显示
            assert password_input.get_attribute("password") == 'true'  # 表示已隐藏
        except Exception as e:
            print(f"❌ Test failed: {e}")
            traceback.print_exc()