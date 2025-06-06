import os
import logging
import tls_client
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# 从环境变量读取必要参数
MACHINE_ID = os.getenv("FC_MACHINE_ID")
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
FC_COOKIE = os.getenv("FC_COOKIE")  # 从环境变量读取 Cookie
FC_COOKIE="sw110xy=b0ghmbtjs42rhf4neg0189o2kk91ktsk"
# 如果未设置环境变量，可直接手动赋值
# FC_COOKIE = "your_freecloud_cookie_here"

# 参数校验
if not all([MACHINE_ID, FC_COOKIE]):
    logging.error("❌ 缺少必要参数：FC_MACHINE_ID 或 FC_COOKIE")
    exit(1)

# URL 定义
RENEW_URL = f"https://freecloud.ltd/server/detail/{MACHINE_ID}/renew"

# 公共请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://freecloud.ltd/member/index",
    "Origin": "https://freecloud.ltd",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": FC_COOKIE
}

# 续费表单数据
RENEW_PAYLOAD = {
    "month": "1",
    "coupon_id": 0,
    "submit": "1"
}

def send_telegram_message(message: str) -> None:
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

def renew_server() -> None:
    logging.info(f"🔄 正在尝试为服务器 {MACHINE_ID} 续费...")
    session = tls_client.Session(client_identifier="chrome_120", random_tls_extension_order=True)

    try:
        response = session.post(RENEW_URL, data=RENEW_PAYLOAD, headers=HEADERS)
        print(response.text)
        try:
            data = response.json()
            message = data.get("msg", "")
            if "3天" in message:
                logging.warning(f"⚠️ 续费状态：{message}")
                send_telegram_message(f"⚠️ {message}")
            elif "续费成功" in message:
                logging.info(f"✅ 续费状态：{message}")
                send_telegram_message(f"✅ 续费状态：{message}")
            else:
                logging.error("⚠️ 未知续费响应，请确认 MACHINE_ID 或 Cookie 是否有效")
                logging.error(f"{message}")
                send_telegram_message(f"{message}")
                exit(1)
        except Exception:
            logging.warning("⚠️ 返回内容不是 JSON，原始响应如下：")
            logging.warning(response.text)
            send_telegram_message(f"⚠️ 无法解析续费响应：\n{response.text}")
            exit(1)
    except Exception as e:
        logging.exception("❌ 续费请求失败：")
        send_telegram_message(f"❌ 续费失败：{str(e)}")
        exit(1)

if __name__ == "__main__":
    renew_server()
