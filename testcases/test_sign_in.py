import pytest
import time
import traceback
import git
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Git 仓库相关设置
REPO_PATH = r"E:\IOT\tests\beatbot"  # 本地 Git 仓库路径
REPO_URL = "https://github.com/ambrosechen1990/beatbot.git"  # GitHub 仓库 URL


@pytest.fixture(scope="module")
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.platform_version = "14"
    options.device_name = "Galaxy S24 Ultra"
    options.app_package = "com.xingmai.tech"
    options.app_activity = "com.xingmai.splash.SplashActivity"
    options.no_reset = True
    options.automation_name = "UiAutomator2"
    options.full_context_list = True

    try:
        driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", options=options)
        yield driver
        driver.quit()
    except Exception as e:
        print(f"❌ Appium driver 启动失败: {str(e)}")
        traceback.print_exc()
        pytest.fail("Appium driver failed to start")


def login(driver):
    try:
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
        )
        sign_in_button.click()
        time.sleep(2)

        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[1]"))
        )
        email_input.send_keys("haoc51888@gmail.com")

        password_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.widget.EditText[2]"))
        )
        password_input.send_keys("csx150128")

        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Sign In']"))
        )
        sign_in_button.click()
        time.sleep(10)

        home_elements = [
            "//android.view.View[@content-desc='Home']",
            "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[4]/android.view.View/android.view.View[1]",
            "//android.widget.TextView[@text='Home']"
        ]

        for home_element in home_elements:
            try:
                driver.find_element(AppiumBy.XPATH, home_element)

                # === 新增操作：退出当前账号 ===
                try:
                    more_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.view.View[@content-desc='More']"))
                    )
                    more_button.click()
                    time.sleep(5)

                    logout_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.ScrollView/android.view.View[12]"))
                    )
                    logout_button.click()
                    time.sleep(1)

                    confirm_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Confirm']"))
                    )
                    confirm_button.click()
                    print("✅ Logout successful.")
                    time.sleep(2)
                except Exception as logout_e:
                    print(f"⚠️ Logout failed: {logout_e}")
                    traceback.print_exc()

                return "Success"
            except:
                continue

        return "Fail"

    except Exception as e:
        print(f"❌ Login Error: {str(e)}")
        traceback.print_exc()
        return "Fail"


def push_to_github():
    try:
        repo = git.Repo(REPO_PATH)

        print("\n📡 当前 Remote 信息：")
        for remote in repo.remotes:
            print(f"🔗 {remote.name} -> {remote.url}")

        untracked_files = repo.untracked_files

        if repo.is_dirty(untracked_files=True) or untracked_files:
            # 手动添加未跟踪文件
            if untracked_files:
                print(f"📥 正在添加未跟踪文件: {untracked_files}")
                repo.index.add(untracked_files)

            repo.index.commit("自动提交：运行测试后提交代码")
            repo.remote(name='origin').push()
            print("✅ 更改已成功推送到 GitHub。")
        else:
            print("🟢 没有新的更改，无需提交。")

    except Exception as e:
        print(f"❌ 推送到 GitHub 时出错: {e}")
        traceback.print_exc()



def test_login(driver):
    result = login(driver)
    assert result == "Success", "❌ Login failed"
    push_to_github()
