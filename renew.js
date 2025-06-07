const fetch = require('node-fetch');
const { URLSearchParams } = require('url');

const USERNAME = process.env.USERNAME;
const PASSWORD = process.env.PASSWORD;
const MACHINE_ID = process.env.FC_MACHINE_ID;

if (!USERNAME || !PASSWORD || !MACHINE_ID) {
  console.error("❌ 缺少环境变量 USERNAME / PASSWORD / FC_MACHINE_ID");
  process.exit(1);
}

const LOGIN_URL = "https://freecloud.ltd/login";
const CONSOLE_URL = "https://freecloud.ltd/member/index";
const RENEW_URL = `https://freecloud.ltd/server/detail/${MACHINE_ID}/renew`;

const userAgents = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
];
const headers = {
  "User-Agent": userAgents[Math.floor(Math.random() * userAgents.length)],
  "Content-Type": "application/x-www-form-urlencoded",
  "Referer": "https://freecloud.ltd/login",
  "Origin": "https://freecloud.ltd"
};

(async () => {
  try {
    const loginPayload = new URLSearchParams({
      username: USERNAME,
      password: PASSWORD,
      mobile: "",
      captcha: "",
      verify_code: "",
      agree: "1",
      login_type: "PASS",
      submit: "1",
    });

    const loginResp = await fetch(LOGIN_URL, {
      method: "POST",
      headers,
      body: loginPayload,
      redirect: "manual"
    });

    // const rawCookie = loginResp.headers.get("set-cookie");
    // if (!rawCookie) {
    //   console.error("❌ 登录失败，未获取 Cookie");
    //   process.exit(1);
    // }

    // const cookie = rawCookie.split(',').map(c => c.split(';')[0]).join('; ');
    const  cookie="sw110xy=f27ko5q5idu93ha4nmsv6jun7skujl15;  07-Jun-2025 18:03:55 GMT"
    await fetch(CONSOLE_URL, {
      method: "GET",
      headers: {
        ...headers,
        Cookie: cookie
      }
    });

    const renewPayload = new URLSearchParams({
      month: "1",
      submit: "1",
      coupon_id: "0"
    });

    const renewResp = await fetch(RENEW_URL, {
      method: "POST",
      headers: {
        ...headers,
        Cookie: cookie,
        "X-Requested-With": "XMLHttpRequest"
      },
      body: renewPayload
    });

    const result = await renewResp.text();

    try {
      const json = JSON.parse(result);
      if (json.msg.includes("3天")) {
        console.log("⚠️ " + json.msg);
      } else {
        console.log("✅ " + json.msg);
      }
    } catch {
      console.error("⚠️ 无法解析续费响应: " + result);
      process.exit(1);
    }
  } catch (err) {
    console.error("❌ 出现异常:", err);
    process.exit(1);
  }
})();
