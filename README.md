# FriendBattle — AI 好友 Battle 系统

![GitHub stars](https://img.shields.io/github/stars/le700/FriendBattle?style=social)
![GitHub forks](https://img.shields.io/github/forks/le700/FriendBattle?style=social)
![GitHub license](https://img.shields.io/github/license/le700/FriendBattle)
![GitHub last commit](https://img.shields.io/github/last-commit/le700/FriendBattle)
![Python version](https://img.shields.io/badge/python-3.12-blue.svg)

FriendBattle 让你克隆两个微信/电报好友的聊天风格，然后用 AI 让他们针对任何话题进行 Battle！甜豆花 vs 咸豆花、原神 vs 王者荣耀、周杰伦 vs 林俊杰...你的好友 AI 替你吵架！

[Website](https://github.com/le700/FriendBattle) · [Docs](https://github.com/le700/FriendBattle) · [Showcase](https://github.com/le700/FriendBattle) · [FAQ](https://github.com/le700/FriendBattle) · [Discord](https://discord.gg/clawd)

---

<div align="center">

🔥 **让你的好友 AI 替你吵架！** 🔥

</div>

## 核心功能

| 功能 | 说明 |
|------|------|
| 🤖 **AI 克隆** | 从微信/Telegram 聊天记录克隆好友语言风格 |
| 🧠 **RAG 记忆库** | 向量数据库存储聊天历史，AI 记得上下文 |
| 🎭 **6 种 Battle 策略** | 杠精、理性、搞笑、激进、和事佬、阴阳怪气 |
| 💬 **实时 Battle** | Web 界面观看两个 AI 互怼 |
| 📱 **社交分享** | 一键生成朋友圈/微博分享图 |
| 📲 **内置微信导出** | 无需安装其他软件，一键导出聊天记录 |
| 🌐 **多 AI 支持** | OpenAI、Claude、Gemini、DeepSeek、智谱AI、本地模型 |
| 🖥️ **三种界面** | CLI 命令行、TUI 终端界面、GUI Web 界面 |
| 👥 **好友管理** | 导入、删除、管理多个好友档案 |

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

# 三种运行方式，任选其一
python friendbattle.py          # 显示菜单选择界面
python friendbattle.py cli      # CLI 命令行
python friendbattle.py tui      # TUI 终端界面
python friendbattle.py gui      # GUI Web 界面
```

## 三种界面模式

### 🖥️ CLI 命令行界面

适合脚本和自动化操作：

```bash
# 列出好友
python friendbattle.py cli list

# 导入聊天记录
python friendbattle.py cli import /path/to/chat.txt "好友名"

# 创建示例好友
python friendbattle.py cli sample

# 删除好友
python friendbattle.py cli delete "好友名"

# 选择好友进行辩论
python friendbattle.py cli select
```

### 📱 TUI 终端用户界面

美观的交互式终端界面：

```
======================================================================
                    FriendBattle
               AI 好友辩论系统
======================================================================

📱 主菜单
----------------------------------------
  1. 📋 查看好友列表
  2. 📤 导入聊天记录
  3. 🗑️ 删除好友
  4. ⚔️ 选择好友辩论
  5. 🎨 创建示例好友
  0. 👋 退出
----------------------------------------

请输入选择 [0-5]:
```

### 🌐 GUI Web 界面

可视化操作，最友好的方式：

启动后访问 http://localhost:3000

## RAG 记忆库系统

FriendBattle 使用向量数据库实现长期记忆：

- **记忆持久化**：聊天历史保存到本地
- **上下文检索**：AI 会记得之前说过的话
- **语义搜索**：基于向量相似度找到相关记忆
- **智能回复**：结合历史对话生成更真实的回复

### 增强的 AI 克隆系统

从聊天记录提取更丰富的特征：

- 📊 语言风格分析
- 😊 表情使用习惯
- 🎤 常用词汇和口头禅
- 🎭 性格特点（乐观/严谨/幽默等）
- 📝 典型对话示例（Few-shot）
- 💬 沟通习惯（问句/感叹词频率）

## 好友管理器

管理你的所有 AI 好友：

- 📤 **导入好友**：从聊天记录创建新好友
- 📋 **查看列表**：显示所有已克隆的好友
- 🗑️ **删除好友**：删除好友及其记忆库
- ⚔️ **选择对战**：选择两个好友开始 Battle
- 📦 **批量管理**：支持多个好友档案

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

## 🎮 示例 Battle

### 📌 辩题：甜豆花 vs 咸豆花

```
【小明 🤬 杠精模式】
豆花当然是甜的好吃！
你告诉我，豆花放糖不香吗？
咸豆花是什么黑暗料理？

【小红 😎 阴阳怪气模式】
哟，咸豆花党急了急了~
也就只有你们才会在豆花里放盐
甜豆花才是永恒的经典好吗！

【小明 🤬 杠精模式】
经典？甜豆花那是甜品好吗！
咸豆花才是正餐！
你早餐吃甜品？

【小红 🧠 理性模式】
从营养学角度，两者各有优势。
北方咸豆花历史悠久，
南方甜豆花口味丰富。
不过...我还是站甜豆花😏
```

---

### 📌 辩题：今晚吃什么

```
【妈 👩 温和模式】
晚上想吃啥？
你做啥我吃啥
不过...清淡点好吗？

【爸 👨 直男模式】
随便
你定
啥都行
（然后挑三拣四）
```

---

<div align="center">
  <b>💡 你的脑洞有多大，Battle 就有多精彩！</b>
</div>

## 项目结构

```
FriendBattle/
├── friendbattle.py      # 主入口脚本
├── src/
│   ├── clone/           # 克隆模块
│   │   ├── cloner.py    # 好友克隆器
│   │   ├── manager.py   # 好友管理器
│   │   ├── memory.py    # RAG 记忆库
│   │   └── parser.py    # 聊天记录解析
│   ├── debate/          # 辩论引擎
│   ├── web/             # Web 界面
│   ├── cli/             # CLI 命令行界面
│   ├── tui/             # TUI 终端界面
│   └── share/           # 分享模块
├── data/                # 数据目录
│   ├── profiles/        # 好友档案
│   └── memory/          # 记忆库存储
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
- [x] CLI 命令行界面
- [x] TUI 终端用户界面
- [x] 好友管理器
- [x] RAG 记忆库系统
- [x] 增强的角色分析
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
