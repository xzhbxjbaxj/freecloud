import os
import sys
import json
import argparse
import requests
from urllib.parse import urlencode
from http.cookiejar import CookieJar
from bs4 import BeautifulSoup

# URL 常量
LOGIN_URL = "https://freecloud.ltd/login"
CONSOLE_URL = "https://freecloud.ltd/member/index"
RENEW_URL_TEMPLATE = "https://freecloud.ltd/server/detail/{}/renew"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://freecloud.ltd/login",
    "Origin": "https://freecloud.ltd",
    "Content-Type": "application/x-www-form-urlencoded",
}


def login(session, username, password):
    print(f"🚀 正在尝试登录用户 {username} ...")
    payload = {
        "username": username,
        "password": password,
        "mobile": "",
        "captcha": "",
        "verify_code": "",
        "agree": "1",
        "login_type": "PASS",
        "submit": "1",
    }

    response = session.post(LOGIN_URL, data=payload, headers=HEADERS)
    if response.status_code != 200:
        print(f"❌ 登录请求失败，状态码: {response.status_code}")
        return False

    html = response.text
    if "退出登录" not in html and "member/index" not in html:
        print("❌ 登录失败，请检查用户名或密码是否正确。")
        return False

    try:
        session.get(CONSOLE_URL, headers=HEADERS)
    except Exception as e:
        print(f"❌ 控制台访问失败: {e}")
        return False

    print("✅ 登录成功！")
    return True


def renew_server(session, machine_id):
    print(f"🔄 正在尝试为服务器 {machine_id} 续费...")
    payload = {
        "month": "1",
        "submit": "1",
        "coupon_id": "0",
    }

    url = RENEW_URL_TEMPLATE.format(machine_id)
    response = session.post(url, data=payload, headers=HEADERS)

    if response.status_code != 200:
        print(f"❌ 续费请求失败，状态码: {response.status_code}")
        return

    try:
        result = response.json()
        msg = result.get("msg", "")
    except Exception:
        print("⚠️ 返回内容不是 JSON，原始响应如下：")
        print(response.text)
        return

    if msg == "请在到期前3天后再续费":
        print(f"⚠️ 续费状态：{msg}")
    elif msg == "续费成功":
        print(f"✅ 续费状态：{msg}")
    else:
        print("❌ 续费失败，请检查 machine_id 是否正确")
        print(f"返回信息：{msg}")
        sys.exit(1)


def load_profiles_from_env():
    raw = os.getenv("FC_PROFILES", "").strip()
    if not raw:
        print("❌ 未提供 FC_PROFILES 环境变量")
        sys.exit(1)

    if not raw.startswith("["):
        raw = f"[{raw}]"

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"❌ 环境变量 JSON 格式错误: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="FreeCloud 自动续费脚本")
    parser.add_argument(
        "-c", "--config", type=str, help="单个用户 JSON 格式，例如 '{\"username\":\"u\",\"password\":\"p\",\"machines\":[123]}'"
    )
    args = parser.parse_args()

    if args.config:
        try:
            profiles = [json.loads(args.config)]
        except json.JSONDecodeError as e:
            print(f"❌ 参数 JSON 格式错误: {e}")
            sys.exit(1)
    else:
        profiles = load_profiles_from_env()

    for profile in profiles:
        username = profile.get("username")
        password = profile.get("password")
        machines = profile.get("machines", [])

        print(f"\n🔑 正在处理用户: {username}")
        session = requests.Session()
        session.cookies = CookieJar()

        if login(session, username, password):
            for mid in machines:
                renew_server(session, mid)


if __name__ == "__main__":
    main()
