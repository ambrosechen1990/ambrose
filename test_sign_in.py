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

    # 验证APP首页登录功能按钮
    def test_signin_01(self):
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

    #验证登录页面到APP首页的“返回键”
    def test_signin_02(self):
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

    #验证正确邮箱+密码，可以登录
    def test_signin_03(self):
        print("Sign In Success")
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
        time.sleep(10)

        # 查找跳转后页面"home"文本元素，，获取其 text 属性
        title = self.driver.find_element(
            AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Home")'
        ).get_attribute("text")
        assert title == "Home"

        #验证“登录”按钮，初始状态为浅色，不可点击





