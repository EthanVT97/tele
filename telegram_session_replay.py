import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options

# 1. Load environment variables from .env
load_dotenv()
STEL_SSID = os.getenv("STEL_SSID")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")  # default fallback

# 2. Validation of required ENV
if not STEL_SSID:
    raise Exception("❌ STEL_SSID cookie value is required in .env")

if not CHROMEDRIVER_PATH or not os.path.isfile(CHROMEDRIVER_PATH):
    raise Exception(f"❌ CHROMEDRIVER_PATH is missing or invalid: {CHROMEDRIVER_PATH}")

# 3. Configure Chrome options for headless environment (Render)
chrome_options = Options()
chrome_options.add_argument("--headless")                   # headless mode (no GUI)
chrome_options.add_argument("--disable-gpu")                # disable GPU for compatibility
chrome_options.add_argument("--no-sandbox")                 # sandbox disable for container environments
chrome_options.add_argument("--disable-dev-shm-usage")      # overcome limited /dev/shm memory in containers
chrome_options.add_argument("--window-size=1280,720")       # set window size
chrome_options.add_argument("--log-level=3")                # reduce logs

# 4. Initialize ChromeDriver service
service = Service(CHROMEDRIVER_PATH)

try:
    # 5. Launch ChromeDriver with options
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("[*] Opening Telegram Web (https://t.me)...")
    driver.get("https://t.me")
    time.sleep(3)

    # 6. Add stel_ssid cookie for session auth
    print("[*] Adding stel_ssid cookie...")
    driver.add_cookie({
        "name": "stel_ssid",
        "value": STEL_SSID,
        "domain": "t.me",
        "path": "/",
        "secure": True,
        "httpOnly": False,
    })

    print("[*] Refreshing page to apply cookie...")
    driver.refresh()
    time.sleep(5)

    # 7. Check login success by finding user profile link
    try:
        profile_button = driver.find_element(By.CSS_SELECTOR, "a[href^='tg://user?id=']")
        print("[✅] Login successful!")
    except NoSuchElementException:
        print("[❌] Login failed or cookie expired.")
        driver.quit()
        exit(1)

    # 8. Click on profile button to open profile page
    print("[*] Opening user profile...")
    profile_button.click()
    time.sleep(5)

    # 9. Extract profile information
    try:
        user_id_element = driver.find_element(By.CSS_SELECTOR, "a[href^='tg://user?id=']")
        user_id = user_id_element.get_attribute("href").split("id=")[1]

        username_element = driver.find_element(By.CSS_SELECTOR, "div[aria-label='User info'] span")
        username = username_element.text

        profile_img = driver.find_element(By.CSS_SELECTOR, "div[class*='tg_head_photo'] img")
        profile_img_url = profile_img.get_attribute("src")

        print(f"User ID: {user_id}")
        print(f"Username: {username}")
        print(f"Profile Image URL: {profile_img_url}")

    except NoSuchElementException:
        print("[❌] Failed to extract profile information.")

except WebDriverException as e:
    print(f"[❌] WebDriver error: {e}")

finally:
    print("[*] Closing browser...")
    try:
        driver.quit()
    except Exception:
        pass
