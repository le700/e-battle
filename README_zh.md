# FriendBattle - AI好友辩论 Battle

让两个AI克隆的好友角色进行精彩 Battle 的开源项目

> 🔥 **让你的微信好友"克隆人"互相对骂，笑到喷饭！**
> ⭐ 一个让 100 万人上瘾的 AI 社交娱乐神器

[![Stars](https://img.shields.io/github/stars/le700/FriendBattle)](https://github.com/le700/FriendBattle/stargazers)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 🎯 一句话介绍

**FriendBattle** 可以让你克隆两个微信/Telegram 好友的聊天风格，然后用 AI 让它们针对任何话题进行 Battle！

- 🤔 "甜豆花好吃还是咸豆花好吃？"
- 😂 "周杰伦和林俊杰谁的歌更好听？"
- 😤 "《原神》和《王者荣耀》谁更火？"

让你的好友 AI 替你吵架！

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🤖 **AI 克隆** | 从微信/Telegram 聊天记录克隆好友语言风格 |
| 🎭 **6 种 Battle 策略** | 杠精、理性、搞笑、激进、和事佬、阴阳怪气 |
| 💬 **实时 Battle** | Web 界面观看两个 AI 互怼 |
| 📱 **社交分享** | 一键生成朋友圈/微博分享图 |
| 🐳 **Docker 部署** | 一行命令，开箱即用 |

## 🚀 30 秒快速开始

### 使用 Docker（推荐）

```bash
# 一行命令，启动 Battle！
docker run -p 3000:3000 le700/friend-battle
```

### 本地运行

```bash
# 克隆项目
git clone https://github.com/le700/FriendBattle.git
cd FriendBattle

# 安装依赖
pip install -r requirements.txt

# 启动！
python src/web/app.py
```

## 📸 使用流程

```
1️⃣  导出微信聊天记录
2️⃣  上传到 FriendBattle
3️⃣  选择两个好友的克隆人
4️⃣  选择 Battle 话题
5️⃣  观看 AI 互怼！
6️⃣  分享到朋友圈！
```

## 🎭 Battle 策略

| 策略 | 风格 | 适合场景 |
|------|------|---------|
| 🤬 **杠精** | 总是反驳对方 | 搞笑对战 |
| 🧠 **理性派** | 摆事实讲道理 | 严肃讨论 |
| 😂 **搞笑** | 金句频出 | 娱乐 Battle |
| 🔥 **激进** | 观点鲜明激烈 | 激烈对战 |
| 🤝 **和事佬** | 试图调解 | 和谐讨论 |
| 😏 **阴阳怪气** | 表面客气实则讽刺 | 高级互怼 |

## 💬 支持的平台

| 平台 | 状态 | 支持格式 |
|------|------|---------|
| ✅ **微信** | 完全支持 | HTML / JSON / TXT |
| ✅ **Telegram** | 完全支持 | JSON |
| 🔄 **QQ** | 开发中 | - |

## 🎬 示例 Battle

```
📌 辩题：甜豆花 vs 咸豆花

【小明 🤬 杠精模式】
豆花当然是甜的好吃！
你告诉我，豆花放糖不香吗？

【小红 🧠 理性模式】
从营养学角度，两者各有优势。
北方咸豆花历史悠久，
南方甜豆花口味丰富。
```

## 🏗️ 技术栈

- **Python 3.12** - 核心语言
- **Flask** - Web 框架
- **PyWxDump** - 微信数据处理
- **Transformers** - AI 模型
- **Docker** - 容器化部署

## 📦 系统要求

**最低配置**：8GB 内存、6GB 显存
**推荐配置**：16GB+ 内存、12GB+ 显存

## 🔥 为什么选 FriendBattle？

- ✅ 完全支持微信
- ✅ 一键 Docker 部署
- ✅ 内置社交分享
- ✅ 6种 Battle 策略

## 📜 许可证

MIT License

## ⚠️ 免责声明

1. 本项目仅供娱乐和学习使用
2. AI 生成内容不代表真实人物观点
3. 请勿用于伤害他人或传播虚假信息
