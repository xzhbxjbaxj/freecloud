import fetch from "node-fetch";
import { URLSearchParams } from "url";

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const USERNAME = process.env.FC_USERNAME;
  const PASSWORD = process.env.FC_PASSWORD;
  const PORT = process.env.FC_PORT;

  if (!USERNAME || !PASSWORD || !PORT) {
    console.error("❌ 缺少环境变量 FC_USERNAME、FC_PASSWORD 或 FC_PORT");
    process.exit(1);
  }

  const LOGIN_URL = "https://freecloud.ltd/login";
  const CONSOLE_URL = "https://freecloud.ltd/member/index";
  const RENEW_URL = `https://freecloud.ltd/server/detail/${PORT}/renew`;

  const userAgents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 12; Pixel 5) Chrome/123.0.0.0 Mobile Safari/537.36"
  ];
  const UA = userAgents[Math.floor(Math.random() * userAgents.length)];

  const headers = {
    "User-Agent": UA,
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://freecloud.ltd/login",
    "Origin": "https://freecloud.ltd",
  };

  const loginPayload = new URLSearchParams({
    username: USERNAME,
    password: PASSWORD,
    agree: "1",
    login_type: "PASS",
    submit: "1",
  });

  const loginResp = await fetch(LOGIN_URL, {
    method: "POST",
    headers,
    body: loginPayload,
    redirect: "manual",
  });

  const rawCookie = loginResp.headers.get("set-cookie");
  if (!rawCookie) {
    console.error("❌ 登录失败，未获得 Cookie");
    process.exit(1);
  }

  const cookie = rawCookie
    .split(',')
    .map(c => c.split(';')[0])
    .join("; ");

  await sleep(500 + Math.floor(Math.random() * 1000));

  await fetch(CONSOLE_URL, {
    method: "GET",
    headers: {
      ...headers,
      Cookie: cookie,
    },
  });

  await sleep(800 + Math.floor(Math.random() * 1000));

  const renewPayload = new URLSearchParams({
    month: "1",
    submit: "1",
    coupon_id: "0",
  });

  const renewResp = await fetch(RENEW_URL, {
    method: "POST",
    headers: {
      ...headers,
      Cookie: cookie,
      "X-Requested-With": "XMLHttpRequest",
    },
    body: renewPayload,
  });

  const text = await renewResp.text();

  try {
    const json = JSON.parse(text);
    if (json.msg.includes("3天")) {
      console.log("⚠️ " + json.msg);
      process.exit(0);
    } else {
      console.log("✅ " + json.msg);
      process.exit(0);
    }
  } catch {
    console.error("❌ 无法解析响应内容:", text);
    process.exit(1);
  }
}

main();
