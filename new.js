import fetch from "node-fetch";

const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
// const FREECLOUD_ACCOUNTS = process.env.FREECLOUD_ACCOUNTS;
// const WORKER_ENDPOINTS = process.env.FREECLOUD_WORKERS?.split(",") || [];



const FREECLOUD_ACCOUNTS={
  "username":"",
  "password":"",
  "port":""
}

const WORKER_ENDPOINTS=["https://solitary-cake-6f69.dj2cubz.workers.dev/"]


if (!FREECLOUD_ACCOUNTS || WORKER_ENDPOINTS.length === 0) {
  console.error("❌ 缺少环境变量：FREECLOUD_ACCOUNTS 或 FREECLOUD_WORKERS");
  process.exit(1);
}

let accounts;
try {
  accounts = JSON.parse(FREECLOUD_ACCOUNTS);
  if (!Array.isArray(accounts) || accounts.length === 0) throw new Error();
} catch {
  console.error("❌ FREECLOUD_ACCOUNTS 格式无效，需为 JSON 数组");
  process.exit(1);
}

console.log(`🧾 共 ${accounts.length} 个账户待处理\n`);

async function notifyTelegram(text) {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) return;

  try {
    await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text,
        parse_mode: "Markdown"
      }),
    });
  } catch (err) {
    console.warn("⚠️ Telegram 通知发送失败", err.message);
  }
}

function formatResultMessage(results) {
  let success = 0, renewSuccess = 0;
  const lines = results.map((res, i) => {
    const base = `#${i + 1} ${res.username}`;
    if (res.error) return `❌ ${base} 错误: ${res.error}`;
    if (res.login && res.renewed) {
      success++; renewSuccess++;
      return `✅ ${base} 登录+续期成功`;
    }
    if (res.login) {
      success++;
      return `⚠️ ${base} 登录成功但续期失败: ${res.message}`;
    }
    return `❌ ${base} 登录失败`;
  });

  const summary = `📦 共 ${results.length} 个账号\n✅ 登录成功: ${success}\n💰 续期成功: ${renewSuccess}\n❌ 错误: ${results.length - success}`;
  return `📢 *FreeCloud 自动续期报告*\n\n${summary}\n\n${lines.join('\n')}\n\n🕐 ${new Date().toLocaleString("zh-CN", { timeZone: "Asia/Shanghai" })}`;
}

async function renewWithWorker(workerUrl, account) {
  try {
    const res = await fetch(workerUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(account),
    });

    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${text}`);

    const json = JSON.parse(text);
    return {
      username: account.username,
      login: json.loginSuccess || false,
      renewed: json.renewSuccess || false,
      message: json.msg || null
    };
  } catch (err) {
    return {
      username: account.username,
      error: err.message
    };
  }
}

async function main() {
  const results = [];

  for (let i = 0; i < accounts.length; i++) {
    const account = accounts[i];
    const endpoint = WORKER_ENDPOINTS[i % WORKER_ENDPOINTS.length];
    console.log(`🔁 正在处理账号 ${account.username} @ ${endpoint}`);
    const result = await renewWithWorker(endpoint, account);
    results.push(result);
  }

  const message = formatResultMessage(results);
  console.log(message);
  await notifyTelegram(message);

  const failures = results.filter(r => r.error || !r.login).length;
  if (failures > 0) process.exit(1);
}

main();
