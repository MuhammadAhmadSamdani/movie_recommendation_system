from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


APP_URL = "http://localhost:8501"
USERNAME = "meow"
WRONG_PASSWORD = "wrongpassword"


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

wait = WebDriverWait(driver, 15)


def visible_inputs():
    return [
        inp for inp in driver.find_elements(By.TAG_NAME, "input")
        if inp.is_displayed() and inp.is_enabled()
    ]


def body_text():
    return driver.find_element(By.TAG_NAME, "body").text.lower()


try:
    # Start from logout/login state
    driver.get(APP_URL + "/?auth=logout")
    driver.get(APP_URL + "/?auth=login")

    wait.until(lambda d: len(visible_inputs()) >= 2)

    inputs = visible_inputs()

    inputs[0].click()
    inputs[0].send_keys(Keys.CONTROL, "a")
    inputs[0].send_keys(USERNAME)

    inputs[1].click()
    inputs[1].send_keys(Keys.CONTROL, "a")
    inputs[1].send_keys(WRONG_PASSWORD)

    login_button = wait.until(
        lambda d: d.find_element(
            By.XPATH,
            "//button[contains(normalize-space(.), 'Login')]"
        )
    )

    login_button.click()

    # Wait until Streamlit error appears OR login form remains visible
    wait.until(
        lambda d: (
            len(d.find_elements(By.CSS_SELECTOR, "[data-testid='stAlert']")) > 0
            or "welcome back" in body_text()
        )
    )

    text = body_text()

    # Main validation:
    # Invalid login should NOT show Logout / Home authenticated page.
    still_on_login = "welcome back" in text or "username or email" in text
    not_logged_in = "logout" not in text and "find your next movie" not in text

    if still_on_login and not_logged_in:
        print("INVALID LOGIN TEST PASSED")
    else:
        print("INVALID LOGIN TEST FAILED")

except Exception as e:
    print("INVALID LOGIN TEST FAILED")
    print("Reason:", e)

finally:
    driver.quit()