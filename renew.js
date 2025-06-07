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

// 多个 URL 轮换使用
const urls = [
  "https://raspy-disk-b126.dj2cubz.workers.dev/",
  "https://round-breeze-41c8.dj2cubz.workers.dev/"
];

// 从中随机选择一个
const url = urls[Math.floor(Math.random() * urls.length)];

const data = {
 // username: USERNAME,
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
    console.log("使用接口:", url);
    console.log("状态码:", response.status);
    console.log("相应内容",response.status)
    console.error("❌ 请求失败:", err);
    process.exit(1);
  }
}

main();
