import os
import time
import json
import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)

USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")

if not USERNAME or not PASSWORD:
    logging.error("❌ 缺少 FC_USERNAME 或 FC_PASSWORD 环境变量。")
    exit(1)

LOGIN_URL = "https://freecloud.ltd/login"

def save_cookies(driver, path="cookies.json"):
    with open(path, "w") as f:
        json.dump(driver.get_cookies(), f)
    logging.info("✅ Cookies 保存成功。")

def login_and_save_cookies():
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(options=options)
    driver.get(LOGIN_URL)
    time.sleep(3)

    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    driver.find_element(By.NAME, "submit").click()
    time.sleep(5)

    if "member/index" not in driver.current_url:
        logging.error("❌ 登录失败，请检查账户信息或页面结构。")
        driver.quit()
        exit(1)

    save_cookies(driver)
    driver.quit()

if __name__ == "__main__":
    login_and_save_cookies()
