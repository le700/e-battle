# 🦞 FriendBattle — AI 好友 Battle 系统

**EXFOLIATE! EXFOLIATE!**

FriendBattle 让你克隆两个微信/电报好友的聊天风格，然后用 AI 让他们针对任何话题进行 Battle！甜豆花 vs 咸豆花、原神 vs 王者荣耀、周杰伦 vs 林俊杰...你的好友 AI 替你吵架！

[Website](https://github.com/le700/FriendBattle) · [Docs](https://github.com/le700/FriendBattle) · [Showcase](https://github.com/le700/FriendBattle) · [FAQ](https://github.com/le700/FriendBattle) · [Discord](https://discord.gg/clawd)

## 核心功能

| 功能 | 说明 |
|------|------|
| 🤖 **AI 克隆** | 从微信/Telegram 聊天记录克隆好友语言风格 |
| 🎭 **6 种 Battle 策略** | 杠精、理性、搞笑、激进、和事佬、阴阳怪气 |
| 💬 **实时 Battle** | Web 界面观看两个 AI 互怼 |
| 📱 **社交分享** | 一键生成朋友圈/微博分享图 |
| 📲 **内置微信导出** | 无需安装其他软件，一键导出聊天记录 |
| 🌐 **多 AI 支持** | OpenAI、Claude、Gemini、DeepSeek、智谱AI、本地模型 |

## 快速开始（TL;DR）

### 📥 下载 EXE（Windows 用户，最简单！）

下载地址：[Releases](https://github.com/le700/FriendBattle/releases)

1. 下载 `FriendBattle.exe`
2. 双击运行
3. 访问 http://localhost:3000

### 🐳 Docker（推荐）

```bash
docker run -p 3000:3000 le700/friend-battle
```

然后访问 http://localhost:3000

### 💻 本地运行

```bash
git clone https://github.com/le700/FriendBattle.git
cd FriendBattle
pip install -r requirements.txt
python src/web/app.py
```

## 支持的 AI 提供商

| 提供商 | 模型 | 说明 |
|--------|------|------|
| **OpenAI** | gpt-3.5-turbo, gpt-4, gpt-4o | 最稳定的选择 |
| **Claude** | claude-3-sonnet, claude-3-opus | 长文本能力强 |
| **Gemini** | gemini-pro, gemini-1.5-pro | Google 出品 |
| **DeepSeek** | deepseek-chat | 免费额度高 |
| **智谱AI** | glm-4, glm-4v | 国内访问快 |
| **本地模型** | Qwen2, Llama-3 | 完全离线 |

## 内置微信导出

**无需安装其他软件！**一键导出聊天记录：
1. 关闭微信
2. 点击"导出微信聊天记录"
3. 自动扫描并导出

如果未找到微信数据，会自动生成示例聊天记录供测试。

## 示例 Battle

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

## 项目结构

```
FriendBattle/
├── src/
│   ├── clone/           # 克隆模块
│   ├── debate/          # 辩论引擎
│   ├── web/             # Web 界面
│   └── share/           # 分享模块
├── config/
│   └── config.yaml      # 配置文件
├── docker/              # Docker 配置
└── requirements.txt     # 依赖列表
```

## 开发路线图

- [x] AI 克隆引擎
- [x] 微信/Telegram 聊天记录支持
- [x] 6 种 Battle 策略
- [x] Web 界面
- [x] Docker 部署
- [x] Windows EXE 打包
- [ ] 语音克隆
- [ ] 实时视频生成
- [ ] 多人 Battle 模式
- [ ] Battle 模板市场

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

## 免责声明

1. 本项目仅供娱乐和学习使用
2. AI 生成内容不代表真实人物观点
3. 请勿用于伤害他人或传播虚假信息
4. 使用本项目即表示同意承担相关责任

---

**⭐ 如果觉得有趣，给个 Star 吧！**

[![Star](https://img.shields.io/github/stars/le700/FriendBattle?style=social)](https://github.com/le700/FriendBattle)
