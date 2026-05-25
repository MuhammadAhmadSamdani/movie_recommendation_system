from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Open browser
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

driver.maximize_window()

try:
    # Open app
    driver.get("http://localhost:8501")

    wait = WebDriverWait(driver, 30)

    # Wait for login inputs
    wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )

    time.sleep(3)

    # Login inputs
    inputs = driver.find_elements(By.TAG_NAME, "input")

    print("Inputs Found:", len(inputs))

    # Username
    inputs[0].send_keys("meow")

    # Password
    inputs[1].send_keys("meow12345")

    time.sleep(2)

    # Find Login button properly
    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Login')]")
        )
    )

    # Scroll
    driver.execute_script(
        "arguments[0].scrollIntoView(true);",
        login_button
    )

    time.sleep(1)

    # Click using JavaScript
    driver.execute_script(
        "arguments[0].click();",
        login_button
    )

    print("✅ Login clicked")

    # Wait after login
    time.sleep(5)

    # Search input
    search_box = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//input[contains(@placeholder,'Search')]"
            )
        )
    )

    # Type movie name
    search_box.send_keys("Batman")

    print("✅ Search typed successfully")

    time.sleep(5)

    # Verify result
    if "Batman" in driver.page_source:
        print("✅ SEARCH TEST PASSED")
    else:
        print("❌ SEARCH TEST FAILED")

except Exception as e:
    print("❌ TEST FAILED")
    print("Message:", e)

    # Screenshot save
    driver.save_screenshot("search_failed.png")
    print("Screenshot saved as search_failed.png")

finally:
    input("Press Enter to close browser...")
    driver.quit()