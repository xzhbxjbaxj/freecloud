import fetch from "node-fetch";

// 从环境变量读取
const USERNAME = process.env.FC_USERNAME;
const PASSWORD = process.env.FC_PASSWORD;
const MACHINE_ID = process.env.FC_MACHINE_ID;
const TG_BOT_TOKEN = process.env.TG_BOT_TOKEN;
const TG_CHAT_ID = process.env.TG_CHAT_ID;

if (!USERNAME || !PASSWORD || !MACHINE_ID) {
  console.error("❌ 缺少环境变量 FC_USERNAME, FC_PASSWORD 或 FC_MACHINE_ID");
  process.exit(1);
}

// 多个 URL 轮换使用
const urls = [
  "https://raspy-disk-b126.dj2cubz.workers.dev/",
  "https://round-breeze-41c8.dj2cubz.workers.dev/"
];

// 随机选择一个 URL
const url = urls[Math.floor(Math.random() * urls.length)];

const data = {
  username: USERNAME,
  password: PASSWORD,
  port: MACHINE_ID
};

/**
 * 向 Telegram 推送消息
 * @param {string} message - 要发送的文本消息
 */
export async function sendTelegramMessage(message) {
  if (!TG_BOT_TOKEN || !TG_CHAT_ID) {
    console.warn("⚠️ 未配置 TG_BOT_TOKEN / TG_CHAT_ID，无法推送消息。");
    return;
  }

  const url = `https://api.telegram.org/bot${TG_BOT_TOKEN}/sendMessage`;

  const payload = {
    chat_id: TG_CHAT_ID,
    text: message,
    parse_mode: "Markdown"
  };

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const text = await response.text();

    if (!response.ok) {
      console.warn(`⚠️ Telegram 消息推送失败: ${text}`);
    } else {
      console.log("✅ Telegram 消息已发送");
    }
  } catch (err) {
    console.error("❌ 推送 Telegram 消息异常：", err);
  }
}

async function main() {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    });

    const text = await response.text();
    console.log("使用接口:", url);
    console.log("状态码:", response.status);

    try {
      const json = JSON.parse(text);
      const msg=json.message;
         if (
        msg.includes("请求体不是有效的 JSON") ||
        msg.includes("缺少用户名、密码或端口号")
      ) {
        console.error(msg);
        sendTelegramMessage(message)    
        process.exit(1); // 让 GitHub Actions 失败退出
      }
      else{
        console.log(msg)
        sendTelegramMessage(message) 
      }
    } catch (err) {
      console.log("⚠️ 返回内容非 JSON:\n", text);
    }

  } catch (err) {
    console.error("❌ 请求失败:", err);
    process.exit(1);
  }
}

main();
