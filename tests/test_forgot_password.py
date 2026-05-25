from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


APP_URL = "http://localhost:8501"

# IMPORTANT:
# Is email ko apne registered account wali email se replace karo.
# Example: agar meow account ka email meow@gmail.com hai, to yehi rakho.
REGISTERED_EMAIL = "meow@gmail.com"


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

wait = WebDriverWait(driver, 15)

try:
    # Direct forgot password page open
    driver.get(APP_URL + "/?auth=forgot")

    # Wait for forgot password input
    wait.until(lambda d: len(d.find_elements(By.TAG_NAME, "input")) >= 1)

    email_input = driver.find_elements(By.TAG_NAME, "input")[0]

    email_input.click()
    email_input.send_keys(Keys.CONTROL, "a")
    email_input.send_keys(REGISTERED_EMAIL)

    # Click Send Reset Code button
    send_button = wait.until(
        lambda d: d.find_element(
            By.XPATH,
            "//button[contains(normalize-space(.), 'Send Reset Code')]"
        )
    )

    send_button.click()

    # Wait for success message
    wait.until(
        lambda d: (
            "verification code sent" in d.page_source.lower()
            or "demo reset code" in d.page_source.lower()
            or "now open the reset password page" in d.page_source.lower()
        )
    )

    print("FORGOT PASSWORD EMAIL SUBMITTED SUCCESSFULLY")
    print("TEST CASE PASSED")

except Exception as e:
    print("TEST CASE FAILED")
    print("Reason:", e)

finally:
    driver.quit()