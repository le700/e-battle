"""
Debate Formatters - 辩论输出格式化器

支持多种输出格式：控制台、JSON、HTML、Markdown等
"""

import json
from abc import ABC, abstractmethod
from typing import List, Dict
from pathlib import Path
from datetime import datetime

from .engine import Debate, DebateTurn


class DebateFormatter(ABC):
    """辩论格式化器基类"""

    @abstractmethod
    def format(self, debate: Debate) -> str:
        """格式化辩论内容"""
        pass

    def save(self, debate: Debate, output_path: Path):
        """保存格式化后的内容"""
        content = self.format(debate)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)


class ConsoleFormatter(DebateFormatter):
    """控制台格式化器"""

    def format(self, debate: Debate) -> str:
        """格式化为控制台输出"""
        lines = []

        lines.append("\n" + "=" * 60)
        lines.append(f"辩论主题：{debate.topic}")
        lines.append(f"辩手1：{debate.debater1} ({debate.skill1})")
        lines.append(f"辩手2：{debate.debater2} ({debate.skill2})")
        lines.append(f"辩论时间：{debate.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60 + "\n")

        turns = [t for t in debate.turns if t.speaker != "System"]

        current_round = 0
        for turn in turns:
            if turn.round_num > current_round:
                current_round = turn.round_num
                lines.append(f"\n--- 第 {turn.round_num} 轮 ---")

            lines.append(f"\n【{turn.speaker}】")
            lines.append(turn.content)

        lines.append("\n" + "=" * 60)
        lines.append(f"辩论结束！")
        if debate.completed_at:
            lines.append(f"完成时间：{debate.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)

        return "\n".join(lines)


class JSONFormatter(DebateFormatter):
    """JSON格式化器"""

    def format(self, debate: Debate) -> str:
        """格式化为JSON"""
        return json.dumps(debate.to_dict(), ensure_ascii=False, indent=2)


class MarkdownFormatter(DebateFormatter):
    """Markdown格式化器"""

    def format(self, debate: Debate) -> str:
        """格式化为Markdown"""
        lines = []

        lines.append(f"# {debate.topic}")
        lines.append("")
        lines.append(f"**正方**：{debate.debater1} ({debate.skill1})")
        lines.append(f"**反方**：{debate.debater2} ({debate.skill2})")
        lines.append(f"**时间**：{debate.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        turns = [t for t in debate.turns if t.speaker != "System"]

        current_round = 0
        for turn in turns:
            if turn.round_num > current_round:
                current_round = turn.round_num
                lines.append(f"\n## 第 {turn.round_num} 轮\n")

            lines.append(f"### {turn.speaker}")
            lines.append("")
            lines.append(turn.content)
            lines.append("")

        lines.append("---")
        lines.append(f"\n*辩论结束 - {len(turns)} 轮对话*\n")

        return "\n".join(lines)


class HTMLFormatter(DebateFormatter):
    """HTML格式化器"""

    def format(self, debate: Debate) -> str:
        """格式化为HTML"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{debate.topic} - AI辩论</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .header .meta {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        .debate-container {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .topic {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .topic h2 {{
            font-size: 1.3em;
        }}
        .round-header {{
            color: #666;
            font-size: 0.85em;
            margin: 25px 0 15px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #eee;
        }}
        .message {{
            margin: 15px 0;
            padding: 15px;
            border-radius: 12px;
        }}
        .message.debater1 {{
            background: #f0f7ff;
            border-left: 4px solid #667eea;
        }}
        .message.debater2 {{
            background: #fff5f5;
            border-left: 4px solid #f5576c;
        }}
        .message .speaker {{
            font-weight: 600;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .message .content {{
            line-height: 1.6;
            color: #333;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #999;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 AI 好友辩论赛</h1>
            <div class="meta">
                {debate.debater1} vs {debate.debater2} | {debate.created_at.strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>

        <div class="debate-container">
            <div class="topic">
                <h2>📌 {debate.topic}</h2>
            </div>
"""

        turns = [t for t in debate.turns if t.speaker != "System"]
        current_round = 0

        for turn in turns:
            if turn.round_num > current_round:
                current_round = turn.round_num
                html += f'<div class="round-header">第 {turn.round_num} 轮</div>\n'

            debater_class = "debater1" if turn.speaker == debate.debater1 else "debater2"
            html += f"""
            <div class="message {debater_class}">
                <div class="speaker">
                    <span>{turn.speaker}</span>
                    <small style="color:#999">{turn.skill_used}</small>
                </div>
                <div class="content">{turn.content}</div>
            </div>
"""

        html += f"""
        </div>

        <div class="footer">
            <p>🤖 由 FriendDebate AI 生成 | {len(turns)} 轮精彩辩论</p>
        </div>
    </div>
</body>
</html>
"""
        return html


class WeChatFormatter(DebateFormatter):
    """微信朋友圈分享格式"""

    def format(self, debate: Debate) -> str:
        """格式化为适合微信分享的内容"""
        lines = []

        lines.append(f"🎭 AI辩论大赛\n")
        lines.append(f"━━━━━━━━━━━━━━━\n")
        lines.append(f"📌 {debate.topic}\n")
        lines.append(f"\n")
        lines.append(f"{debate.debater1} vs {debate.debater2}\n")
        lines.append(f"\n")
        lines.append(f"━━━━━━━━━━━━━━━\n")

        turns = [t for t in debate.turns if t.speaker != "System"][:8]

        for i, turn in enumerate(turns, 1):
            lines.append(f"💬 {turn.speaker}：")
            content = turn.content[:100] + "..." if len(turn.content) > 100 else turn.content
            lines.append(f"   {content}\n")

        if len([t for t in debate.turns if t.speaker != "System"]) > 8:
            lines.append(f"...\n")

        lines.append(f"━━━━━━━━━━━━━━━\n")
        lines.append(f"🤖 共 {len([t for t in debate.turns if t.speaker != 'System'])} 轮精彩辩论\n")
        lines.append(f"✨ 用 FriendDebate 体验更多有趣辩论！")

        return "\n".join(lines)


def get_formatter(format_type: str) -> DebateFormatter:
    """
    根据格式类型获取格式化器

    Args:
        format_type: 格式类型 (console, json, markdown, html, wechat)

    Returns:
        对应的格式化器
    """
    formatters = {
        "console": ConsoleFormatter,
        "json": JSONFormatter,
        "markdown": MarkdownFormatter,
        "html": HTMLFormatter,
        "wechat": WeChatFormatter,
    }

    formatter_class = formatters.get(format_type.lower())
    if not formatter_class:
        raise ValueError(f"未知的格式类型：{format_type}")

    return formatter_class()
