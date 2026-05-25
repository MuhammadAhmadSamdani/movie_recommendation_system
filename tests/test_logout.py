from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


APP_URL = "http://localhost:8501"
USERNAME = "meow"
PASSWORD = "meow12345"


driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

wait = WebDriverWait(driver, 15)

try:
    driver.get(APP_URL)

    # Wait for login page inputs
    wait.until(lambda d: len(d.find_elements(By.TAG_NAME, "input")) >= 2)

    inputs = driver.find_elements(By.TAG_NAME, "input")

    # Enter username/email
    inputs[0].click()
    inputs[0].send_keys(Keys.CONTROL, "a")
    inputs[0].send_keys(USERNAME)

    # Enter password
    inputs[1].click()
    inputs[1].send_keys(Keys.CONTROL, "a")
    inputs[1].send_keys(PASSWORD)

    # Click login button
    login_button = wait.until(
        lambda d: d.find_element(
            By.XPATH,
            "//button[contains(normalize-space(.), 'Login')]"
        )
    )

    login_button.click()

    # Wait until login is successful
    wait.until(
        lambda d: (
            "logout" in d.page_source.lower()
            or "find your next movie" in d.page_source.lower()
            or "movie recommendation" in d.page_source.lower()
        )
    )

    print("LOGIN SUCCESSFUL")

    # IMPORTANT:
    # Your app.py logout works through query param ?auth=logout
    # So we directly open that logout route.
    driver.get(APP_URL + "/?auth=logout")

    # Wait until login page appears again
    wait.until(
        lambda d: (
            len(d.find_elements(By.TAG_NAME, "input")) >= 2
            and "login" in d.page_source.lower()
        )
    )

    print("LOGOUT SUCCESSFUL")
    print("TEST CASE PASSED")

except Exception as e:
    print("TEST CASE FAILED")
    print("Reason:", e)

finally:
    driver.quit()