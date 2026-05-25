import os
import sys
import time
import traceback
from datetime import datetime
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


APP_URL = "http://localhost:8501"
USERNAME = "meow"
PASSWORD = "meow12345"

SCREENSHOT_DIR = "selenium_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)

driver.maximize_window()
wait = WebDriverWait(driver, 40)

step = "START"


def take_screenshot(name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCREENSHOT_DIR, f"{timestamp}_{name}.png")
    driver.save_screenshot(path)
    print("Screenshot saved:", path)


def save_html(name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCREENSHOT_DIR, f"{timestamp}_{name}.html")

    with open(path, "w", encoding="utf-8") as file:
        file.write(driver.page_source)

    print("HTML saved:", path)


def page_text():
    try:
        return driver.find_element(By.TAG_NAME, "body").text.lower()
    except Exception:
        return ""


def visible_inputs():
    return [
        input_box
        for input_box in driver.find_elements(By.TAG_NAME, "input")
        if input_box.is_displayed() and input_box.is_enabled()
    ]


def clear_and_type(element, value):
    element.click()

    select_key = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL

    element.send_keys(select_key, "a")
    element.send_keys(Keys.BACKSPACE)
    element.send_keys(value)


def print_debug_links_and_buttons():
    print("\n========== LINKS FOUND ==========")
    links = driver.find_elements(By.TAG_NAME, "a")
    print("Total links:", len(links))

    for index, link in enumerate(links):
        text = link.text.strip()
        href = link.get_attribute("href")
        class_name = link.get_attribute("class")
        print(f"[LINK {index}] text={text!r} | href={href!r} | class={class_name!r}")

    print("\n========== BUTTONS FOUND ==========")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print("Total buttons:", len(buttons))

    for index, button in enumerate(buttons):
        text = button.text.strip()
        class_name = button.get_attribute("class")
        print(f"[BUTTON {index}] text={text!r} | class={class_name!r}")


def find_movie_anchor_link():
    """
    Best case:
    Movie card should be an anchor link like:
    <a class="movie-card" href="?view=details&movie_id=123">
    """

    selectors = [
        "a.movie-card",
        "a[href*='movie_id']",
        "a[href*='movie']",
        "a[href*='details']",
        "a[href*='detail']",
        "a[href*='id=']",
    ]

    bad_words = [
        "auth=login",
        "auth=logout",
        "auth=forgot",
        "auth=reset",
        "auth=register",
        "view=home",
        "view=account",
        "view=help",
        "cat=trending",
        "cat=popular",
        "cat=top_rated",
        "cat=now_playing",
    ]

    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)

        for element in elements:
            if not element.is_displayed():
                continue

            href = element.get_attribute("href")
            text = element.text.strip()

            if not href:
                continue

            href_lower = href.lower()

            if any(bad in href_lower for bad in bad_words):
                continue

            print("\nMovie anchor found")
            print("Selector:", selector)
            print("Text:", text)
            print("Href:", href)

            return element, href

    return None, None


def find_movie_button():
    """
    Fallback case:
    If app uses Streamlit buttons instead of anchor links.
    Example button text:
    Details
    View Details
    More Info
    Open
    """

    buttons = driver.find_elements(By.TAG_NAME, "button")

    preferred_words = [
        "view details",
        "details",
        "more info",
        "open",
        "watch",
        "explore",
    ]

    bad_words = [
        "login",
        "logout",
        "send reset code",
        "register",
        "sign up",
        "forgot",
        "reset",
    ]

    for button in buttons:
        if not button.is_displayed() or not button.is_enabled():
            continue

        text = button.text.strip().lower()

        if not text:
            continue

        if any(bad in text for bad in bad_words):
            continue

        if any(word in text for word in preferred_words):
            print("\nMovie button found")
            print("Button text:", text)
            return button

    return None


try:
    step = "OPEN_LOGIN_PAGE"

    driver.get(APP_URL + "/?auth=logout")
    time.sleep(1)

    driver.get(APP_URL + "/?auth=login")
    take_screenshot("login_page")

    step = "WAIT_LOGIN_INPUTS"

    wait.until(lambda d: len(visible_inputs()) >= 2)

    step = "FILL_LOGIN_FORM"

    inputs = visible_inputs()

    clear_and_type(inputs[0], USERNAME)
    clear_and_type(inputs[1], PASSWORD)

    take_screenshot("login_form_filled")

    step = "CLICK_LOGIN_BUTTON"

    login_button = wait.until(
        lambda d: d.find_element(
            By.XPATH,
            "//button[contains(normalize-space(.), 'Login')]"
        )
    )

    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", login_button)

    step = "WAIT_HOME_PAGE_AFTER_LOGIN"

    wait.until(
        lambda d: (
            "logout" in page_text()
            or "home" in page_text()
            or "trending" in page_text()
            or "popular" in page_text()
            or "movie" in page_text()
        )
    )

    print("\nLOGIN SUCCESSFUL")
    print("Current URL after login:", driver.current_url)

    take_screenshot("after_login")
    save_html("after_login")

    step = "DEBUG_HOME_PAGE"

    print_debug_links_and_buttons()

    step = "FIND_MOVIE_CARD_OR_BUTTON"

    movie_link_element, movie_url = find_movie_anchor_link()

    if movie_url:
        step = "OPEN_MOVIE_DETAIL_BY_LINK"

        full_movie_url = urljoin(APP_URL, movie_url)

        print("\nOpening movie detail URL:")
        print(full_movie_url)

        driver.get(full_movie_url)

    else:
        print("\nNo movie anchor link found. Trying movie detail button...")

        movie_button = find_movie_button()

        if not movie_button:
            take_screenshot("no_movie_card_or_button_found")
            save_html("no_movie_card_or_button_found")
            raise Exception(
                "No movie detail link or button found. "
                "Your app is not exposing movie cards as clickable links/buttons."
            )

        step = "OPEN_MOVIE_DETAIL_BY_BUTTON"

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", movie_button)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", movie_button)

    time.sleep(3)

    take_screenshot("movie_detail_opened")
    save_html("movie_detail_opened")

    print("\nCurrent URL after opening movie detail:", driver.current_url)

    step = "VERIFY_MOVIE_DETAIL_PAGE"

    text = page_text()

    print("\n========== MOVIE DETAIL PAGE TEXT SAMPLE ==========")
    print(text[:1500])

    if "could not load details" in text:
        raise Exception("Movie detail page opened, but app shows: Could not load details")

    error_words = [
        "error loading",
        "failed to load",
        "movie not found",
        "no movie found",
    ]

    if any(error_word in text for error_word in error_words):
        raise Exception("Movie detail page opened, but error text was found")

    expected_detail_words = [
        "overview",
        "rating",
        "release",
        "genre",
        "similar movies",
        "recommended for you",
        "now showing",
        "description",
        "cast",
        "duration",
    ]

    if any(word in text for word in expected_detail_words):
        print("\nMOVIE DETAIL TEST PASSED")
        take_screenshot("movie_detail_test_passed")
    else:
        raise Exception(
            "Movie detail page opened, but expected movie detail content was not found."
        )

except Exception as e:
    print("\nMOVIE DETAIL TEST FAILED")
    print("Failed step:", step)
    print("Reason:", e)

    try:
        print("Current URL:", driver.current_url)
        take_screenshot(f"failed_at_{step}")
        save_html(f"failed_at_{step}")
    except Exception as screenshot_error:
        print("Could not save screenshot/html:", screenshot_error)

    traceback.print_exc()

finally:
    driver.quit()