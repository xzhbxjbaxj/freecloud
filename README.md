# FreeCloud 自动续费脚本

## 项目简介
本脚本可实现 FreeCloud 平台服务器的自动化续费操作，支持 Telegram 消息通知功能。

## 功能特性
- ✅ 自动化登录与 Cookie 维护
- ⚡ 智能续费操作（支持自定义续费周期）
- 📨 多通道通知（Telegram 机器人集成）
- 📊 实时日志追踪（INFO/WARNING/ERROR分级）

## 环境要求
Python 3.8+ 

## 教程
✅ 一、功能简介
这个项目通过 GitHub Actions 自动运行 login.py 脚本，实现 FreeCloud 账号自动签到或续期，支持：

每 2 天自动运行一次（可手动执行）

Telegram 通知签到结果（可选）

🛠️ 二、准备工作
1. 你需要准备：
- 一个 GitHub 账号（注册：https://github.com）
- 一个 FreeCloud 账号（用于获取登录信息）
（可选）一个 Telegram Bot Token 和 Chat ID（用于通知）

📝 三、详细操作步骤
第一步：Fork 仓库（复制一份到自己账号）
1.打开项目页面（如果是别人的项目，地址形如 https://github.com/xxx/FreeCloud-Auto-Renew）
2.点击右上角的 Fork，选择你自己的账号即可。

第二步：添加 Secrets（存放账号信息）
- 1.进入你 Fork 后的仓库主页。
- 2.点击 Settings → 左侧 Secrets and variables → Actions。
- 3.点击 New repository secret 添加以下内容：
                 
| 名称              | 含义                 | 示例或说明                 |
| --------------- | ------------------ | --------------------- |
| `FC_USERNAME`   | FreeCloud 登录邮箱     | `example@gmail.com`   |
| `FC_PASSWORD`   | FreeCloud 密码       | `yourpassword123`     |
| `FC_MACHINE_ID` | 设备ID（一般是一个固定字符串）   | 登录 FreeCloud 后查看设备绑定页 |
| `TG_BOT_TOKEN`  | Telegram 机器人令牌（可选） | `123456:ABC-DEF...`   |
| `TG_CHAT_ID`    | Telegram 聊天 ID（可选） | `123456789`           |

📌 提示：TG 信息非必须，不填也能运行。

第三步：查看脚本运行（首次手动执行）
- 1.打开你的仓库 → 点击顶部 Actions 标签页。
- 2.你会看到 FreeCloud Auto Renew，点击进入。
- 3.点击右侧 Run workflow → 点击绿色按钮手动运行一次。

💡成功后可在 Actions 日志中查看签到结果。

第四步：设置自动运行（已默认配置）
在 .github/workflows/xxx.yml 文件中已经设置：

- cron: "0 0 */2 * *"
表示：每 2 天自动执行一次（UTC 时间 0:00），不需你手动改动。

💬 常见问题
Q1：如何获取 FC_MACHINE_ID？
答：登录 FreeCloud 官网，在设备管理处查看当前登录设备的唯一 ID，复制即可。

Q2：怎么获取 Telegram 通知 Token 和 Chat ID？
答：@BotFather 创建 Bot，获取 Token
向你的机器人发送一条消息，然后访问下面链接查看你的chat_id：https://api.telegram.org/bot<你的Token>/getUpdates

✅ 教程完结
现在，你的 FreeCloud 自动签到系统已经搭建完成！它将：
每两天自动运行一次
使用你设置的账号自动签到
可选通知到 Telegram
如需进一步定制或调试，可以编辑 login.py 或 workflow 文件。
pip install cloudscraper requests
