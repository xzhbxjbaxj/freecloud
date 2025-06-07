import fetch from "node-fetch";

// 从环境变量读取
const USERNAME = process.env.FC_USERNAME;
const PASSWORD = process.env.FC_PASSWORD;
const MACHINE_ID = process.env.FC_MACHINE_ID;

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
        process.exit(1); // 让 GitHub Actions 失败退出
      }
      else{
        console.log(msg)
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
