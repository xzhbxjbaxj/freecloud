import os
import httpx
import logging
from typing import Optional
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# 从环境变量读取账号信息
USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")
MACHINE_ID = os.getenv("FC_MACHINE_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# 参数校验
if not all([USERNAME, PASSWORD, MACHINE_ID]):
    logging.error("环境变量 FC_USERNAME / FC_PASSWORD / FC_MACHINE_ID 缺失，请配置后重试。")
    exit(1)

# URL 定义
LOGIN_URL = "https://freecloud.ltd/login"
CONSOLE_URL = "https://freecloud.ltd/member/index"
RENEW_URL = f"https://freecloud.ltd/server/detail/{MACHINE_ID}/renew"

# 公共请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://freecloud.ltd/login",
    "Origin": "https://freecloud.ltd",
    "Content-Type": "application/x-www-form-urlencoded"
}

# 登录表单数据
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

# 续费表单数据
RENEW_PAYLOAD = {
    "month": "1",
    "submit": "1",
    "coupon_id": 0
}

def send_telegram_message(message: str) -> None:
    """
    向 Telegram 推送通知消息
    """
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        logging.warning("⚠️ 未配置 TG_BOT_TOKEN / TG_CHAT_ID，无法推送消息。")
        return

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            logging.warning(f"⚠️ Telegram 消息推送失败: {response.text}")
    except Exception:
        logging.exception("❌ 推送 Telegram 消息异常：")

def login_session() -> Optional[httpx.Client]:
    """
    使用 httpx 模拟登录并返回会话对象
    """
    logging.info("🚀 正在尝试使用 httpx 登录 FreeCloud...")

    try:
        client = httpx.Client(follow_redirects=True, headers=HEADERS)
        resp = client.post(LOGIN_URL, data=LOGIN_PAYLOAD)
        if resp.status_code != 200:
            logging.error(f"❌ 登录请求失败，状态码: {resp.status_code}")
            send_telegram_message(f"❌ 登录请求失败，状态码: {resp.status_code}")
            exit(1)
            return None

        if "退出登录" not in resp.text and "member/index" not in resp.text:
            logging.error("❌ 登录失败，用户名或密码错误或被识别为机器人。")
            send_telegram_message("❌ 登录失败，用户名或密码错误或被识别为机器人。")
            exit(1)
            return None

        client.get(CONSOLE_URL)

        logging.info("✅ 登录成功！")
        send_telegram_message("✅ FreeCloud 登录成功！")
        return client

    except Exception as e:
        logging.exception("❌ 登录出错：")
        send_telegram_message(f"❌ 登录出错：{str(e)}")
        exit(1)
        return None

def renew_server(session: httpx.Client) -> None:
    """
    使用已登录的 session 发起续费请求
    """
    logging.info(f"🔄 正在尝试为服务器 {MACHINE_ID} 续费...")
    try:
        response = session.post(RENEW_URL, data=RENEW_PAYLOAD)
        response.raise_for_status()

        try:
            data = response.json()
            message = data.get("msg", "")
            if message == '请在到期前3天后再续费':
                logging.warning(f"⚠️ 续费状态：{message}")
                send_telegram_message(f"⚠️ {message}")
            elif message == '续费成功':
                logging.info(f"✅ 续费状态：{message}")
                send_telegram_message(f"✅ 续费状态：{message}")
            else:
                logging.error(f"⚠️ 其他状态：{message}")
                send_telegram_message(f"⚠️ {message}")
                exit(1)
        except Exception:
            logging.warning("⚠️ 返回内容不是 JSON，原始响应如下：")
            logging.warning(response.text)
            send_telegram_message(f"⚠️ 无法解析续费响应：\n{response.text}")
            exit(1)

    except Exception as e:
        logging.exception("❌ 续费失败：")
        send_telegram_message(f"❌ 续费失败：{str(e)}")
        exit(1)

if __name__ == "__main__":
    session = login_session()
    if session:
        renew_server(session)
