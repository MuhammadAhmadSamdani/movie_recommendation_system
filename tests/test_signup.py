from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

driver.maximize_window()

try:
    # Open signup page
    driver.get("http://localhost:8501/?auth=signup")

    wait = WebDriverWait(driver, 30)

    # Wait for all inputs
    wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )

    inputs = driver.find_elements(By.TAG_NAME, "input")

    print("Inputs Found:", len(inputs))

    # Fill form
    inputs[0].send_keys("tingu")
    inputs[1].send_keys("tingu@gmail.com")
    inputs[2].send_keys("tingu12345")
    inputs[3].send_keys("tingu12345")

    time.sleep(3)

    # Find Create Account button
    button = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//button[contains(., 'Create Account')]"
            )
        )
    )

    # Scroll to button
    driver.execute_script(
        "arguments[0].scrollIntoView(true);",
        button
    )

    time.sleep(2)

    # Click using JavaScript
    driver.execute_script(
        "arguments[0].click();",
        button
    )

    time.sleep(5)

    print("✅ BUTTON CLICKED")

    # Verify success
    page = driver.page_source

    if "Now login" in page:
        print("✅ SIGNUP TEST PASSED")
    else:
        print("❌ SIGNUP FAILED")

        driver.save_screenshot("signup_error.png")

except Exception as e:
    print("❌ TEST FAILED")
    print("Error:", str(e))

    driver.save_screenshot("real_error.png")

finally:
    input("Press Enter to close browser...")
    driver.quit()