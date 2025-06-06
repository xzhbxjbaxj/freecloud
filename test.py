import os
import time
import logging
import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 环境变量
USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")
MACHINE_ID = os.getenv("FC_MACHINE_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

LOGIN_URL = "https://freecloud.ltd/login"
RENEW_URL = f"https://freecloud.ltd/server/detail/{MACHINE_ID}/renew"

def send_telegram(message):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        logging.warning("未配置 Telegram 相关信息")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT_ID, "text": message},
            timeout=10,
        )
    except Exception as e:
        logging.warning(f"Telegram 消息发送失败: {e}")

def login_and_get_session():
    logging.info("启动浏览器进行模拟登录...")
    options = uc.ChromeOptions()
    options.add_argument("--headless")  # 如需调试，可注释掉这行
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = uc.Chrome(options=options)

    try:
        driver.get(LOGIN_URL)
        time.sleep(2)

        # 填写用户名和密码
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.NAME, "agree").click()
        driver.find_element(By.NAME, "submit").click()

        time.sleep(5)

        if "member/index" not in driver.current_url:
            logging.error("❌ 登录失败，页面未跳转至用户中心")
            send_telegram("❌ 登录失败，FreeCloud 用户名或密码可能错误")
            driver.quit()
            return None

        logging.info("✅ 登录成功，获取 cookies 中...")
        send_telegram("✅ 登录成功，准备续费")

        session = requests.Session()
        for cookie in driver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])

        return session

    except Exception as e:
        logging.exception("❌ 登录异常")
        send_telegram(f"❌ 登录出错：{str(e)}")
        return None
    finally:
        driver.quit()

def renew(session):
    logging.info("发起续费请求...")
    headers = {
        "Referer": f"https://freecloud.ltd/server/detail/{MACHINE_ID}",
        "User-Agent": "Mozilla/5.0",
    }

    data = {
        "month": "1",
        "submit": "1",
        "coupon_id": 0
    }

    try:
        resp = session.post(RENEW_URL, headers=headers, data=data)
        resp.raise_for_status()
        try:
            result = resp.json()
            msg = result.get("msg", "无返回消息")
        except:
            msg = resp.text[:100]

        if "续费成功" in msg:
            logging.info("✅ 续费成功")
            send_telegram("✅ FreeCloud 续费成功")
        elif "请在到期前" in msg:
            logging.info(f"⚠️ 暂不能续费: {msg}")
            send_telegram(f"⚠️ {msg}")
        else:
            logging.error(f"❌ 续费失败: {msg}")
            send_telegram(f"❌ 续费失败: {msg}")
    except Exception as e:
        logging.exception("❌ 续费请求失败")
        send_telegram(f"❌ 请求失败：{str(e)}")

if __name__ == "__main__":
    if not all([USERNAME, PASSWORD, MACHINE_ID]):
        logging.error("❌ 环境变量 FC_USERNAME / FC_PASSWORD / FC_MACHINE_ID 缺失")
        exit(1)

    session = login_and_get_session()
    if session:
        renew(session)
