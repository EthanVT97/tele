import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

# Load environment variables
load_dotenv()
STEL_SSID = os.getenv("STEL_SSID")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

if not STEL_SSID:
    raise Exception("❌ STEL_SSID cookie value is required in .env")

if not CHROMEDRIVER_PATH or not os.path.isfile(CHROMEDRIVER_PATH):
    raise Exception(f"❌ CHROMEDRIVER_PATH is missing or invalid: {CHROMEDRIVER_PATH}")

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--window-size=1280,720")
chrome_options.add_argument("--log-level=3")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("[*] Opening Telegram Web...")
    driver.get("https://t.me")
    time.sleep(3)

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

    try:
        profile_button = driver.find_element(By.CSS_SELECTOR, "a[href^='tg://user?id=']")
        print("[+] Login successful!")
    except NoSuchElementException:
        print("[-] Login failed or cookie expired.")
        driver.quit()
        exit(1)

    print("[*] Opening user profile...")
    profile_button.click()
    time.sleep(5)

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
        print("[-] Failed to extract profile information.")

finally:
    print("[*] Closing browser...")
    driver.quit()
