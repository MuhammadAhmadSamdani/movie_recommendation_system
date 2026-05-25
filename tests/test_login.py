from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time

# Open Chrome
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

driver.maximize_window()

try:
    # Open app
    driver.get("http://localhost:8501")

    wait = WebDriverWait(driver, 30)

    # Wait for inputs
    wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )

    time.sleep(3)

    # Get all input fields
    inputs = driver.find_elements(By.TAG_NAME, "input")

    print("Inputs Found:", len(inputs))

    # Username
    inputs[0].send_keys("meow")

    # Password
    inputs[1].send_keys("meow12345")

    time.sleep(2)

    # Find Login button specifically
    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Login')]")
        )
    )

    # Scroll to button
    driver.execute_script(
        "arguments[0].scrollIntoView(true);",
        login_button
    )

    time.sleep(1)

    # Click using JS
    driver.execute_script(
        "arguments[0].click();",
        login_button
    )

    time.sleep(5)

    # Verify login success
    if "Logout" in driver.page_source:
        print("✅ LOGIN TEST PASSED")
    else:
        print("❌ LOGIN FAILED")

except Exception as e:
    print("❌ TEST FAILED")
    print("Message:", e)

    # Screenshot save
    driver.save_screenshot("failed_login.png")
    print("Screenshot saved as failed_login.png")

finally:
    input("Press Enter to close browser...")
    driver.quit()