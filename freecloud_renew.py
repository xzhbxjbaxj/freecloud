import os
import json
import logging
import requests

logging.basicConfig(level=logging.INFO)

MACHINE_ID = os.getenv("FC_MACHINE_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

RENEW_URL = f"https://freecloud.ltd/server/detail/{MACHINE_ID}/renew"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": f"https://freecloud.ltd/server/detail/{MACHINE_ID}",
}

RENEW_PAYLOAD = {
    "month": "1",
    "submit": "1",
    "coupon_id": 0
}

def send_telegram_message(msg: str):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        logging.warning("⚠️ 未配置 TG_BOT_TOKEN 或 TG_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logging.error(f"Telegram 推送失败: {e}")

def load_cookies(path="cookies.json"):
    with open(path, "r") as f:
        raw = json.load(f)
    return {c["name"]: c["value"] for c in raw}

def renew():
    if not MACHINE_ID:
        logging.error("❌ 未设置 FC_MACHINE_ID")
        return

    cookies = load_cookies()
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.update(cookies)

    logging.info("🔄 开始续费请求...")
    try:
        r = session.post(RENEW_URL, data=RENEW_PAYLOAD)
        r.raise_for_status()
        try:
            data = r.json()
            msg = data.get("msg", "")
            logging.info(f"📢 续费结果: {msg}")
            send_telegram_message(f"📢 续费状态: {msg}")
        except:
            logging.warning("⚠️ 返回非 JSON 内容")
            logging.warning(r.text)
            send_telegram_message(f"⚠️ 无法解析返回内容:\n{r.text}")
    except Exception as e:
        logging.error(f"❌ 请求异常: {e}")
        send_telegram_message(f"❌ 续费失败: {e}")

if __name__ == "__main__":
    renew()
