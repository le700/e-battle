# 微信聊天记录导出指南

本指南将帮助你从微信导出聊天记录，以便在 FriendDebate 中克隆好友角色。

## 目录

- [方法一：使用 PyWxDump（推荐）](#方法一使用-pywxdump推荐)
- [方法二：手动导出 HTML](#方法二手动导出-html)
- [方法三：导出为 JSON](#方法三导出为-json)
- [方法四：使用第三方工具](#方法四使用第三方工具)
- [常见问题](#常见问题)

---

## 方法一：使用 PyWxDump（推荐）

PyWxDump 是最强大的微信数据提取工具，支持解密数据库并导出聊天记录。

### 1.1 安装 PyWxDump

```bash
# 使用 pip 安装
pip install -U pywxdump

# 或使用项目提供的工具
python scripts/wechat_extractor.py install
```

### 1.2 获取微信信息

首先，确保你的电脑已经登录微信，然后运行：

```bash
python scripts/wechat_extractor.py info
```

这将显示：
- 微信昵称
- 微信账号
- 数据库密钥（KEY）
- 数据库路径

**重要**：记录输出的 `key`（数据库密钥），后续步骤需要用到。

### 1.3 解密数据库

使用获取的密钥解密微信数据库：

```bash
python scripts/wechat_extractor.py decrypt \
  -k "你的数据库密钥" \
  -i "/path/to/encrypted/Msg.db" \
  -o "data/wechat_decrypted"
```

### 1.4 浏览聊天记录

启动 Web 界面浏览聊天记录：

```bash
python scripts/wechat_extractor.py browse \
  -merge "data/wechat_decrypted/merged/merge_all.db" \
  --allow-lan
```

然后在浏览器中访问 http://127.0.0.1:5000 查看。

### 1.5 导出指定好友的聊天记录

```bash
python scripts/wechat_extractor.py export \
  -u "好友的微信ID或昵称" \
  -o "data/chatlogs" \
  -msg "data/wechat_decrypted/merged/Msg.db" \
  -micro "data/wechat_decrypted/merged/MicroMsg.db" \
  -media "data/wechat_decrypted/merged/MediaMSG.db"
```

这将在 `data/chatlogs` 目录下生成好友的聊天记录文件。

---

## 方法二：手动导出 HTML

如果不想使用 PyWxDump，可以使用微信桌面版手动导出聊天记录。

### 2.1 导出步骤

1. 打开微信桌面版并登录
2. 进入与好友的聊天窗口
3. 点击右上角 `...` 菜单
4. 选择「导出聊天记录」
5. 选择「包括图片/语音/视频等媒体」或「仅文字」
6. 选择保存位置

### 2.2 文件格式

导出的文件可能是：
- **HTML 格式**：`.html` 文件，包含完整的聊天内容
- **TXT 格式**：`.txt` 纯文本文件
- **JSON 格式**：`.json` 结构化数据

### 2.3 放置文件

将导出的文件放入项目的 `data/chatlogs/` 目录：

```bash
# 假设导出的文件名为 xiaoming.html
mv xiaoming.html FriendDebate/data/chatlogs/
```

---

## 方法三：导出为 JSON

如果你能访问微信数据库，可以使用以下方法导出 JSON 格式：

### 3.1 使用数据库查询

```python
import sqlite3
import json
from datetime import datetime

def export_chat_to_json(db_path, talker, output_path):
    """
    从微信数据库导出指定联系人的聊天记录为 JSON
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT CreateTime, StrContent, StrTalker, IsSelf
        FROM ChatHistory
        WHERE StrTalker = ?
        ORDER BY CreateTime
    """, (talker,))

    messages = []
    for row in cursor.fetchall():
        timestamp, content, talker, is_self = row
        messages.append({
            "id": len(messages) + 1,
            "date": datetime.fromtimestamp(timestamp / 1000).isoformat(),
            "text": content,
            "type": 1,
            "sender": "me" if is_self else talker
        })

    conn.close()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"messages": messages}, f, ensure_ascii=False, indent=2)

    print(f"✅ 导出完成：{output_path}")

# 使用示例
export_chat_to_json(
    db_path="data/wechat_decrypted/Msg.db",
    talker="好友的微信ID",
    output_path="data/chatlogs/friend.json"
)
```

---

## 方法四：使用第三方工具

### 4.1 微信聊天记录导出工具

市场上有多款工具可以帮助导出微信聊天记录：

| 工具名称 | 平台 | 特点 |
|---------|------|------|
| 卓师兄 | Android | 简单易用，图形界面 |
| 楼月微信聊天记录导出 | Windows | 支持多种格式导出 |
| WeChatMsg | Windows | 开源，支持多种导出格式 |
| WechatExport | macOS | macOS 平台专用 |

### 4.2 使用 WeChatMsg（推荐）

WeChatMsg 是一个开源的微信聊天记录导出工具：

1. 下载地址：https://github.com/CHXYA/WeChatMsg
2. 运行程序并登录微信
3. 选择要导出的好友
4. 选择导出格式（推荐 JSON 或 HTML）
5. 导出到 `data/chatlogs/` 目录

---

## 常见问题

### Q1: PyWxDump 无法获取数据库密钥？

**原因**：微信需要处于登录状态才能获取密钥。

**解决方案**：
1. 确保微信桌面版已登录
2. 尝试重启微信和程序
3. 检查微信版本是否支持

### Q2: 导出的文件显示乱码？

**解决方案**：
- 确保文件编码为 UTF-8
- 使用支持编码选择的工具重新导出
- 或手动转换编码

### Q3: 聊天记录太少影响克隆效果？

**建议**：
- 至少需要 100 条以上对话
- 越多越好，建议 5000+ 条
- 选择语言风格鲜明的好友

### Q4: 如何找到好友的微信 ID？

**方法**：
1. 在微信桌面版，好友资料页查看
2. 通过 PyWxDump 的聊天浏览功能查看
3. 在数据库中查询 `ChatRoomMember` 表

### Q5: 隐私和安全注意事项？

**重要提醒**：
- ✅ 仅使用自己的聊天记录
- ✅ 获得好友同意后再克隆其形象
- ✅ 妥善保管数据库密钥
- ❌ 不要上传包含隐私的数据到网络
- ❌ 不要用于伤害他人或传播虚假信息

---

## 下一步

导出聊天记录后，你可以：

1. **创建 AI 克隆角色**
   ```bash
   python src/cli.py create \
     --chat-log data/chatlogs/friend.json \
     --name "好友昵称" \
     --platform wechat
   ```

2. **开始辩论**
   ```bash
   python src/cli.py debate \
     --debater1 friend1 \
     --debater2 friend2 \
     --topic "今天吃什么？"
   ```

3. **使用 Web 界面**
   ```bash
   python src/web/app.py
   ```
   然后访问 http://localhost:3000

---

## 技术支持

如果遇到问题：

1. 查看 [FAQ 文档](./FAQ.md)
2. 提交 [GitHub Issue](https://github.com/le700/FriendDebate/issues)
3. 加入微信群交流

---

*本指南最后更新于 2026-05-15*
