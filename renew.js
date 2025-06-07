// renew.js

import fetch from "node-fetch";

// 从环境变量读取
const USERNAME = process.env.FC_USERNAME;
const PASSWORD = process.env.FC_PASSWORD;
const MACHINE_ID = process.env.FC_MACHINE_ID;

if (!USERNAME || !PASSWORD || !MACHINE_ID) {
  console.error("❌ 缺少环境变量 FC_USERNAME, FC_PASSWORD 或 FC_MACHINE_ID");
  process.exit(1);
}

const url = "https://raspy-disk-b126.dj2cubz.workers.dev/";

const data = {
  username: USERNAME,
  password: PASSWORD,
  port: MACHINE_ID, // 或 machine_id
};

async function main() {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const text = await response.text();
    console.log("状态码:", response.status);
    console.log("响应文本:\n", text);
  } catch (err) {
    console.error("❌ 请求失败:", err);
    process.exit(1);
  }
}

main();
