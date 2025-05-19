import cloudscraper
import os

# 环境变量中读取凭证（也可以改为从环境变量读取）
USERNAME = os.getenv("FC_USERNAME")
PASSWORD = os.getenv("FC_PASSWORD")
MACHINE_ID=os.getenv("FC_MACHINE_ID")

# 登录与续费 URL
LOGIN_URL   = "https://freecloud.ltd/login"
CONSOLE_URL = "https://freecloud.ltd/member/index"
RENEW_URL   = "https://freecloud.ltd/server/detail/"+MACHINE_ID+"/renew"

# 通用请求头（模拟正常浏览器）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.0.0 Safari/537.36",
    "Referer": "https://freecloud.ltd/login",
    "Origin": "https://freecloud.ltd",
    "Content-Type": "application/x-www-form-urlencoded"
}

# 登录表单字段
LOGIN_PAYLOAD = {
    "username":      USERNAME,
    "password":      PASSWORD,
    "mobile":        "",
    "captcha":       "",
    "verify_code":   "",
    "agree":         "1",
    "login_type":    "PASS",
    "submit":        "1",
}

# 续费表单字段
RENEW_PAYLOAD = {
    "month": "1",
    "submit": "1",
    "coupon_id": 0
}


def login_session():
    """使用 cloudscraper 模拟登录并返回带 Cookie 的 scraper 会话"""
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    # 登录获取 cookie
    response = scraper.post(LOGIN_URL, data=LOGIN_PAYLOAD, headers=HEADERS, allow_redirects=True)
    response.raise_for_status()

    # 访问控制台页以完成跳转和 session 激活
    console_resp = scraper.get(CONSOLE_URL)
    console_resp.raise_for_status()

    return scraper


def renew_server(session):
    """使用已登录的 session 提交续费请求"""
    response = session.post(RENEW_URL, data=RENEW_PAYLOAD, headers=HEADERS)
    response.raise_for_status()
    try:
        resp_json = response.json()
        print("✅", resp_json.get("msg", "续费完成"))
    except Exception as e:
        print("⚠️ 返回非 JSON 内容，原始响应：")
        print(response.text)


if __name__ == "__main__":
    try:
        sess = login_session()
        renew_server(sess)
    except Exception as e:
        print("❌ 请求失败:", e)
