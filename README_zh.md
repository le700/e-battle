# FriendBattle — AI好友Battle系统

<p align="center">
  <img src="https://img.shields.io/github/stars/le700/FriendBattle?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/le700/FriendBattle?style=social" alt="GitHub forks">
  <img src="https://img.shields.io/github/license/le700/FriendBattle" alt="GitHub license">
  <img src="https://img.shields.io/github/last-commit/le700/FriendBattle" alt="GitHub last commit">
  <img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python version">
  <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="Build Status">
</p>

<p align="center">
  <strong>🔥 让你的微信好友"克隆人"互相对骂，笑到喷饭！</strong><br>
  <strong>⭐ 一个让你停不下来的AI社交娱乐神器</strong>
</p>

---

<div align="center">

## 🎯 一句话介绍

**FriendBattle** 可以让你克隆两个微信好友的聊天风格，然后用AI让它们针对任何话题进行Battle！

[🔥 快速开始](#-快速开始) · [✨ 核心功能](#-核心功能) · [🎭 Battle策略](#-battle-策略) · [📖 使用指南](#-使用指南)

</div>

## 📸 效果展示

> 💡 想象一下：把你平时最逗比的两个朋友的聊天记录导进来，然后让AI克隆他们互怼，效果拔群！

<table>
<tr>
<td><strong>辩题：甜豆花 vs 咸豆花</strong></td>
<td><strong>辩题：程序员该不该写注释</strong></td>
</tr>
<tr>
<td>
<pre>
【小明 🤬 杠精模式】
豆花当然是甜的好吃！
你告诉我，豆花放糖不香吗？
咸豆花是什么黑暗料理？

【小红 😏 阴阳怪气模式】
哟，咸豆花党急了急了~
也就只有你们才会在豆花里放盐
甜豆花才是永恒的经典好吗！
</pre>
</td>
<td>
<pre>
【老张 🧑‍💻 工程师模式】
写注释是职业素养！
你自己写的代码三个月后
还看得懂吗？

【小李 🤪 摸鱼模式】
能跑就行，注释那么多
老板以为我在写小说呢？
代码就是最好的文档！
</pre>
</td>
</tr>
</table>

---

## 🎭 示例Battle

**辩题：甜豆花 vs 咸豆花**

```
【小明 🤬 杠精模式】
豆花当然是甜的好吃！
你告诉我，豆花放糖不香吗？
咸豆花是什么黑暗料理？

【小红 😏 阴阳怪气模式】
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

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🤖 **AI克隆** | 从微信聊天记录克隆好友语言风格 |
| 🧠 **RAG记忆库** | 可选向量数据库，AI记得上下文 |
| 🎭 **9种Battle策略** | 杠精、理性、搞笑、激进、和事佬、阴阳怪气、学者、毒舌、摸鱼 |
| 💬 **实时Battle** | Web界面观看两个AI互怼 |
| 📱 **内置微信导出** | 无需安装其他软件，一键导出聊天记录 |
| 🌐 **多AI支持** | OpenAI、Claude、Gemini、DeepSeek、智谱AI、本地模型 |
| 🖥️ **三种界面** | CLI命令行、TUI终端界面、GUI Web界面 |
| 👥 **好友管理** | 导入、删除、管理多个好友档案 |

---

## 🚀 快速开始

### 💻 本地运行（推荐）

```bash
git clone https://github.com/le700/FriendBattle.git
cd FriendBattle

# 快速安装（只安装核心依赖）
pip install -r requirements.txt

# 三种运行方式，任选其一
python friendbattle.py          # 菜单选择界面
python friendbattle.py cli      # CLI命令行
python friendbattle.py tui      # TUI终端界面
python friendbattle.py gui      # GUI Web界面
```

### 📥 Windows用户（最简单）

下载EXE版本（Coming Soon）：[Releases](https://github.com/le700/FriendBattle/releases)

1. 下载 `FriendBattle.exe`
2. 双击运行
3. 访问 http://localhost:3000

---

## 🎭 Battle策略

FriendBattle提供9种精心设计的辩论策略：

| 策略 | 风格 | 适合场景 |
|------|------|---------|
| 🤬 **杠精** | 总是反驳对方 | 搞笑对战 |
| 🧠 **理性派** | 摆事实讲道理 | 严肃讨论 |
| 😂 **搞笑** | 金句频出 | 娱乐Battle |
| 🔥 **激进** | 观点鲜明激烈 | 激烈对战 |
| 🤝 **和事佬** | 试图调解 | 和谐讨论 |
| 😏 **阴阳怪气** | 表面客气实则讽刺 | 高级互怼 |
| 🎓 **学者** | 引经据典，书生气 | 学术讨论 |
| 🗡️ **毒舌** | 一针见血，说话带刺 | 激烈互怼 |
| 😴 **摸鱼** | 敷衍但有趣 | 轻松闲聊 |

---

## 📖 使用指南

### 1️⃣ 微信聊天记录导入

我们提供了完全独立的微信数据导入功能，**无需安装任何其他软件**！

**操作流程：**

1. **完全关闭微信** - 确保微信没有在运行
2. **重新打开微信并登录** - 使用手机扫码登录
3. **打开FriendBattle的Web界面** - 访问 `/wechat` 页面
4. **点击"重新检测密钥"** - 系统会自动提取微信数据库密钥
5. **选择好友** - 从列表中选择要导入的好友
6. **点击"导入"** - 一键创建AI好友克隆

**支持的聊天记录格式：**
- 微信官方HTML导出
- JSON格式
- TXT文本格式
- 直接从微信数据库读取（推荐）

### 2️⃣ 创建AI好友

```bash
# 从聊天记录导入
python friendbattle.py cli import /path/to/chat.txt "好友名"

# 创建示例好友
python friendbattle.py cli sample
```

### 3️⃣ 开始Battle！

选择两个好友，设置辩题，开始观看AI互怼！

---

## 🔧 可选高级功能

需要更强大的功能？按需安装：

### 🧠 RAG记忆库（向量检索）

```bash
pip install chromadb>=0.4.20 sentence-transformers>=2.2.0
```

### 🤖 本地模型支持

```bash
pip install transformers>=4.35.0 torch>=2.0.0 accelerate>=0.25.0
```

---

## 🖥️ 三种界面模式

### 📱 TUI终端界面（最推荐）

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

### 🖥️ CLI命令行界面

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

### 🌐 GUI Web界面

可视化操作，最友好的方式：

启动后访问 http://localhost:3000

---

## 🏗️ 项目结构

```
FriendBattle/
├── friendbattle.py          # 主入口脚本
├── src/
│   ├── clone/               # 克隆模块
│   │   ├── cloner.py        # 好友克隆器
│   │   ├── manager.py       # 好友管理器
│   │   ├── memory.py        # RAG记忆库
│   │   └── parser.py        # 聊天记录解析
│   ├── debate/              # 辩论引擎
│   │   ├── engine.py        # 辩论引擎核心
│   │   └── skills.py        # 辩论策略库
│   ├── web/                 # Web界面
│   │   ├── app.py           # Flask应用
│   │   └── templates/       # HTML模板
│   ├── wechat_scanner/      # 微信数据库扫描
│   ├── wechat_image/        # 微信图片解密
│   └── wechat_integration/  # 微信集成接口
├── data/                    # 数据目录
│   ├── profiles/            # 好友档案
│   └── chatlogs/            # 聊天记录
├── config/
│   └── config.yaml          # 配置文件
└── requirements.txt         # 依赖列表（核心依赖）
```

---

## 🌐 支持的AI提供商

| 提供商 | 模型 | 说明 |
|--------|------|------|
| **OpenAI** | gpt-3.5-turbo, gpt-4, gpt-4o | 最稳定的选择 |
| **Claude** | claude-3-sonnet, claude-3-opus | 长文本能力强 |
| **Gemini** | gemini-pro, gemini-1.5-pro | Google出品 |
| **DeepSeek** | deepseek-chat | 免费额度高 |
| **智谱AI** | glm-4, glm-4v | 国内访问快 |
| **本地模型** | Qwen2, Llama-3 | 完全离线 |

---

## 📖 使用指南

### 1️⃣ 第一步：导出聊天记录

使用内置的微信导出功能，或手动准备聊天记录文件（支持TXT、JSON等格式）。

### 2️⃣ 第二步：克隆好友

```bash
python friendbattle.py cli clone
```
选择"导入聊天记录"，然后：
- 选择平台（txt/json/wechat/telegram）
- 选择要克隆的聊天记录文件
- 命名好友档案

### 3️⃣ 第三步：开始Battle

```bash
python friendbattle.py gui   # 推荐，Web界面最直观
```
或者使用CLI：
```bash
python friendbattle.py cli debate
```
选择两个已克隆的好友，设置辩题，选择Battle策略，开始观看！

### 💡 高级功能

- **RAG记忆库**：可选安装chromadb，让AI更好地理解上下文
- **多AI切换**：可以随时切换不同的AI提供商
- **策略混合**：可以为每个辩论者选择不同的策略

---

## ❓ FAQ - 常见问题

### Q: 需要微信Root吗？
**A:** 不需要！本项目可以直接读取微信数据库，也支持导入导出的聊天记录文件。

### Q: 哪些AI提供商支持？
**A:** OpenAI、Claude、Gemini、DeepSeek、智谱AI，还有本地模型！

### Q: 聊天记录会上传到服务器吗？
**A:** 绝对不会！所有数据都在本地处理，保护你的隐私安全。

### Q: 没有微信聊天记录能玩吗？
**A:** 可以！内置了多种预设性格，直接就能让AI互怼！

### Q: EXE版本什么时候出？
**A:** GitHub Actions已经在自动打包了，很快就能在Release页下载！

---

## 🤝 参与贡献

欢迎提交Issue和Pull Request！让我们一起让这个项目更好玩！

1. Fork本仓库
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个Pull Request

---

## 📝 开发路线图

- [x] AI克隆引擎
- [x] 微信聊天记录支持（完全独立实现）
- [x] Web界面
- [x] Windows EXE打包
- [x] CLI命令行界面
- [x] TUI终端用户界面
- [x] 好友管理器
- [x] RAG记忆库系统（可选）
- [x] 增强的角色分析
- [x] 优化依赖，快速安装
- [x] 9种Battle策略
- [x] 独立的微信数据库扫描
- [x] 微信图片解密
- [ ] 语音克隆
- [ ] 实时视频生成
- [ ] 多人Battle模式
- [ ] Battle模板市场

---

## 📜 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## ⚠️ 免责声明

1. 本项目仅供娱乐和学习使用
2. AI生成内容不代表真实人物观点
3. 请勿用于伤害他人或传播虚假信息
4. 使用本项目即表示同意承担相关责任

---

<div align="center">

## 💡 你的脑洞有多大，Battle就有多精彩！

**⭐ 如果觉得有趣，给个 Star 吧！**

[![Star](https://img.shields.io/github/stars/le700/FriendBattle?style=social)](https://github.com/le700/FriendBattle)

</div>
