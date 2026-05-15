# FriendBattle - AI好友辩论 Battle

让两个AI克隆的好友角色进行精彩 Battle 的开源项目

> 🔥 **让你的微信好友"克隆人"互相对骂，笑到喷饭！**
> ⭐ 一个让 100 万人上瘾的 AI 社交娱乐神器

[![Stars](https://img.shields.io/github/stars/le700/FriendBattle)](https://github.com/le700/FriendBattle/stargazers)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

![FriendBattle Demo](assets/demo.png)

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
| 📲 **内置微信导出** | **无需安装其他软件**，一键导出聊天记录 |
| 🌐 **多 AI 支持** | OpenAI、Claude、Gemini、DeepSeek、智谱AI、本地模型 |

## 🚀 30 秒快速开始

### 📥 方式一：直接下载 EXE（推荐）

**Windows 用户最简单！**

1. 下载 `FriendBattle.exe`
2. 双击运行
3. 访问 http://localhost:3000

**下载地址**：[Releases](https://github.com/le700/FriendBattle/releases)

### 🐳 方式二：使用 Docker

```bash
# 一行命令，启动 Battle！
docker run -p 3000:3000 le700/friend-battle
```

然后访问 http://localhost:3000

### 💻 方式三：本地运行

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
    ↓
2️⃣  上传到 FriendBattle
    ↓
3️⃣  选择两个好友的克隆人
    ↓
4️⃣  选择 Battle 话题
    ↓
5️⃣  观看 AI 互怼！
    ↓
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

## 🌐 支持的 AI 提供商

| 提供商 | 模型 | 说明 |
|--------|------|------|
| **OpenAI** | gpt-3.5-turbo, gpt-4, gpt-4o | 最稳定的选择 |
| **Claude** | claude-3-sonnet, claude-3-opus | 长文本能力强 |
| **Gemini** | gemini-pro, gemini-1.5-pro | Google 出品 |
| **DeepSeek** | deepseek-chat | 免费额度高 |
| **智谱AI** | glm-4, glm-4v | 国内访问快 |
| **本地模型** | Qwen2, Llama-3 | 完全离线 |

### 📲 内置微信导出

**无需安装其他软件！**一键导出聊天记录：
1. 关闭微信
2. 点击"导出微信聊天记录"
3. 自动扫描并导出

如果未找到微信数据，会自动生成示例聊天记录供测试。

## 🎬 示例 Battle

```
📌 辩题：甜豆花 vs 咸豆花

【小明 🤬 杠精模式】
豆花当然是甜的好吃！
你告诉我，豆花放糖不香吗？
豆腐脑不加糖能吃？

【小红 🧠 理性模式】
从营养学角度，两者各有优势。
北方咸豆花历史悠久，
南方甜豆花口味丰富。
我认为不应该简单比较。
```

## 🏗️ 技术栈

- **Python 3.12** - 核心语言
- **Flask** - Web 框架
- **PyWxDump** - 微信数据处理
- **Transformers** - AI 模型
- **Docker** - 容器化部署

## 📦 系统要求

**最低配置**：
- 8GB 内存
- 6GB 显存（GPU）
- 20GB 磁盘

**推荐配置**：
- 16GB+ 内存
- 12GB+ 显存（RTX 4070+）

## 🔥 为什么选 FriendBattle？

| 对比 | 其他项目 | FriendBattle |
|------|---------|-------------|
| 微信支持 | ❌ 不支持 | ✅ 完全支持 |
| 部署难度 | ⚠️ 复杂 | ✅ 一键部署 |
| 社交分享 | ❌ 没有 | ✅ 内置分享 |
| Battle 策略 | ❌ 没有 | ✅ 6种策略 |

## 📄 项目结构

```
FriendBattle/
├── src/
│   ├── clone/          # AI 克隆模块
│   ├── debate/         # Battle 引擎
│   ├── web/            # Web 界面
│   └── share/          # 分享模块
├── docker/             # Docker 配置
├── docs/               # 文档
├── assets/             # 资源文件
└── requirements.txt
```

## 🛤️ 开发路线图

- [x] AI 克隆引擎
- [x] 微信/Telegram 聊天记录支持
- [x] 6 种 Battle 策略
- [x] Web 界面
- [x] Docker 部署
- [ ] 语音克隆
- [ ] 视频生成
- [ ] 多人 Battle
- [ ] Battle 模板市场

## 🤝 贡献

欢迎提交 Issue 和 PR！

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE)

## ⚠️ 免责声明

1. 本项目仅供娱乐和学习使用
2. AI 生成内容不代表真实人物观点
3. 请勿用于伤害他人或传播虚假信息
4. 使用本项目即表示同意承担相关责任

---

**⭐ 如果觉得好玩，给个 Star 吧！**

[![Star](https://img.shields.io/github/stars/le700/FriendBattle?style=social)](https://github.com/le700/FriendBattle)
