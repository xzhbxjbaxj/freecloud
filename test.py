import os
import tls_client
import logging
import requests
from typing import Optional

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# 读取环境变量
USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")
MACHINE_ID = os.getenv("FC_MACHINE_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

if not all([USERNAME, PASSWORD, MACHINE_ID]):
    logging.error("❌ 缺少环境变量，请确保设置了 FC_USERNAME / FC_PASSWORD / FC_MACHINE_ID")
    exit(1)

# URL
LOGIN_URL = "https://freecloud.ltd/login"
CONSOLE_URL = "https://freecloud.ltd/member/index"
RENEW_URL = f"https://freecloud.ltd/server/detail/{MACHINE_ID}/renew"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Origin": "https://freecloud.ltd",
    "Referer": "https://freecloud.ltd/login",
    "Content-Type": "application/x-www-form-urlencoded"
}

LOGIN_PAYLOAD = {
    "username": USERNAME,
    "password": PASSWORD,
    "mobile": "",
    "captcha": "",
    "verify_code": "",
    "agree": "1",
    "login_type": "PASS",
    "submit": "1",
}

RENEW_PAYLOAD = {
    "month": "1",
    "submit": "1",
    "coupon_id": 0
}


def send_telegram_message(message: str):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        logging.warning("⚠️ 未配置 TG_BOT_TOKEN 或 TG_CHAT_ID，跳过 Telegram 通知。")
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        res = requests.post(url, data=data)
        if res.status_code != 200:
            logging.warning(f"⚠️ Telegram 消息推送失败：{res.text}")
    except Exception as e:
        logging.error(f"❌ 推送 Telegram 异常：{e}")


def login_session() -> Optional[tls_client.Session]:
    logging.info("🚀 正在登录 FreeCloud ...")
    session = tls_client.Session(client_identifier="chrome_120")
    try:
        resp = session.post(LOGIN_URL, data=LOGIN_PAYLOAD, headers=HEADERS)
        if resp.status_code != 200 or "退出登录" not in resp.text:
            logging.error("❌ 登录失败，请检查用户名密码")
            send_telegram_message("❌ FreeCloud 登录失败，请检查账号信息")
            exit(1)
        logging.info("✅ 登录成功！")
        send_telegram_message("✅ FreeCloud 登录成功！")
        return session
    except Exception as e:
        logging.exception("❌ 登录异常：")
        send_telegram_message(f"❌ 登录异常：{e}")
        exit(1)


def renew_server(session: tls_client.Session):
    logging.info(f"🔄 尝试为机器 {MACHINE_ID} 续费...")
    try:
        resp = session.post(RENEW_URL, data=RENEW_PAYLOAD, headers=HEADERS)
        if resp.status_code != 200:
            logging.error(f"❌ 续费请求失败，状态码：{resp.status_code}")
            send_telegram_message("❌ FreeCloud 续费请求失败")
            exit(1)

        try:
            result = resp.json()
            msg = result.get("msg", "")
            if msg == "请在到期前3天后再续费":
                logging.warning(f"⚠️ {msg}")
                send_telegram_message(f"⚠️ {msg}")
            elif msg == "续费成功":
                logging.info(f"✅ {msg}")
                send_telegram_message(f"✅ FreeCloud 续费成功！")
            else:
                logging.error(f"❌ 未知返回消息：{msg}")
                send_telegram_message(f"❌ 续费失败：{msg}")
                exit(1)
        except Exception:
            logging.error("⚠️ 返回内容非 JSON")
            logging.error(resp.text)
            send_telegram_message("⚠️ 无法解析续费响应")
            exit(1)
    except Exception as e:
        logging.exception("❌ 续费请求异常：")
        send_telegram_message(f"❌ FreeCloud 续费失败：{e}")
        exit(1)


if __name__ == "__main__":
    sess = login_session()
    if sess:
        renew_server(sess)
