from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import time


APP_URL = "http://localhost:8501"

EXISTING_USERNAME = "meow"
NEW_EMAIL = f"duplicate_meow_{int(time.time())}@example.com"
PASSWORD = "Meow12345"


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

wait = WebDriverWait(driver, 15)


def visible_inputs():
    return [
        inp for inp in driver.find_elements(By.TAG_NAME, "input")
        if inp.is_displayed() and inp.is_enabled()
    ]


def page_text():
    return driver.find_element(By.TAG_NAME, "body").text.lower()


try:
    # Make sure user is logged out
    driver.get(APP_URL + "/?auth=logout")

    # Open signup page
    driver.get(APP_URL + "/?auth=signup")

    # Wait for signup inputs
    wait.until(lambda d: len(visible_inputs()) >= 4)

    inputs = visible_inputs()

    # Username: already existing username
    inputs[0].click()
    inputs[0].send_keys(Keys.CONTROL, "a")
    inputs[0].send_keys(EXISTING_USERNAME)

    # Email: new email, so only username duplicate is tested
    inputs[1].click()
    inputs[1].send_keys(Keys.CONTROL, "a")
    inputs[1].send_keys(NEW_EMAIL)

    # Password
    inputs[2].click()
    inputs[2].send_keys(Keys.CONTROL, "a")
    inputs[2].send_keys(PASSWORD)

    # Confirm Password
    inputs[3].click()
    inputs[3].send_keys(Keys.CONTROL, "a")
    inputs[3].send_keys(PASSWORD)

    # Click Create Account
    create_button = wait.until(
        lambda d: d.find_element(
            By.XPATH,
            "//button[contains(normalize-space(.), 'Create Account')]"
        )
    )

    create_button.click()

    # Wait for error alert or page response
    wait.until(
        lambda d: (
            len(d.find_elements(By.CSS_SELECTOR, "[data-testid='stAlert']")) > 0
            or "already" in page_text()
            or "exists" in page_text()
            or "taken" in page_text()
            or "registered" in page_text()
            or "now login" in page_text()
            or "account created" in page_text()
        )
    )

    text = page_text()

    duplicate_error_found = (
        "already" in text
        or "exists" in text
        or "taken" in text
        or "registered" in text
        or "username" in text and len(driver.find_elements(By.CSS_SELECTOR, "[data-testid='stAlert']")) > 0
    )

    signup_success_found = (
        "account created" in text
        or "now login with your new username" in text
    )

    if duplicate_error_found and not signup_success_found:
        print("DUPLICATE USERNAME TEST PASSED")
    else:
        print("DUPLICATE USERNAME TEST FAILED")

except Exception as e:
    print("DUPLICATE USERNAME TEST FAILED")
    print("Reason:", e)

finally:
    driver.quit()