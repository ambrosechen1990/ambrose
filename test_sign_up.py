import pytest
import time
import traceback
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from appium.options.android import UiAutomator2Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        print(f"Error while starting Appium driver: {str(e)}")
        traceback.print_exc()
        pytest.fail("Appium driver failed to start")

def generate_email(suffix):
    return f"hc{suffix}@gmail.com"

def logout(driver):
    try:
        # Perform logout actions (replace with actual logout actions based on your app)
        logout_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.Button[@text='Logout']"))  # Adjust XPath as needed
        )
        logout_button.click()
        time.sleep(3)
        print("Logged out successfully.")
    except Exception as e:
        print(f"Logout Error: {str(e)}")
        traceback.print_exc()

def register(driver, country, email_suffix_number):
    try:
        # Registration steps (same as your original registration logic)
        sign_up_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View[2]"))
        )
        sign_up_button.click()
        time.sleep(5)

        region_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[1]"))
        )
        region_button.click()
        time.sleep(5)

        search_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText"))
        )
        search_input.send_keys(country)

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[1]/android.view.View"))
        )
        search_button.click()
        time.sleep(5)

        while True:
            email = generate_email(email_suffix_number )

            email_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText"))
            )
            email_input.clear()
            email_input.send_keys(email)

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.CheckBox"))
            ).click()

            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.XPATH, "//androidx.compose.ui.platform.ComposeView/android.view.View/android.view.View/android.view.View/android.view.View[2]"))
            ).click()
            time.sleep(3)

            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((AppiumBy.XPATH, "//android.view.ViewGroup/android.view.View/android.view.View"))
                )
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Cancel']"))
                ).click()
                email_suffix_number += 1

                box_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.CheckBox"))
                )
                box_button.click()
                continue
            except:
                break

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[1]"))
        ).send_keys("csx150128")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[2]"))
        ).send_keys("csx150128")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.view.View/android.view.View/android.view.View/android.view.View[1]"))
        ).click()
        time.sleep(5)

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText"))
        ).send_keys("beatbot")

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.view.View/android.view.View/android.view.View/android.view.View[2]"))
        ).click()
        time.sleep(5)

        home_elements = [
            "//android.view.View[@content-desc='Home']",
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
                        EC.element_to_be_clickable(
                            (AppiumBy.XPATH, "//android.widget.ScrollView/android.view.View[12]"))
                    )
                    logout_button.click()
                    time.sleep(1)

                    confirm_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.TextView[@text='Confirm']"))
                    )
                    confirm_button.click()
                    print("Logout successful.")
                    time.sleep(2)
                except Exception as logout_e:
                    print(f"Logout failed: {logout_e}")
                    traceback.print_exc()

                return "Success"
            except:
                continue

        return "Fail"

    except Exception as e:
        print(f"Register Error: {str(e)}")
        traceback.print_exc()
        return "Fail"

def test_register(driver):
    countries = ["France", "United States of America","U.S. Virgin Islands"]
    email_suffix_number = 1001

    for country in countries:
        result = register(driver, country, email_suffix_number)
        if result == "Success":
            print(f"Registration Test for {country} Passed")
        else:
            print(f"Registration Test for {country} Failed")

