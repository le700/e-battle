"""
WeChat Chat Parser - 微信聊天记录解析器

支持多种微信聊天记录导出格式
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeChatMessage:
    """微信消息"""
    sender: str
    content: str
    timestamp: datetime
    msg_type: int = 1
    is_self: bool = False


class WeChatHTMLParser:
    """微信 HTML 导出格式解析器"""

    def parse(self, html_path: Path) -> List[WeChatMessage]:
        """解析微信导出的 HTML 格式"""
        messages = []

        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("请安装 BeautifulSoup: pip install beautifulsoup4")
            return messages

        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        chat_area = soup.find("div", class_="chat")
        if not chat_area:
            chat_area = soup.find("div", id="chatArea")

        if not chat_area:
            return messages

        message_divs = chat_area.find_all("div", class_="message")

        for div in message_divs:
            sender_elem = div.find("span", class_="sender")
            content_elem = div.find("div", class_="content")

            if not content_elem:
                continue

            sender = sender_elem.text.strip() if sender_elem else "Unknown"
            content = content_elem.text.strip()

            time_elem = div.find("span", class_="time")
            if time_elem:
                try:
                    timestamp = datetime.strptime(time_elem.text.strip(), "%Y-%m-%d %H:%M:%S")
                except:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()

            is_self = "me" in div.get("class", [])

            messages.append(WeChatMessage(
                sender=sender,
                content=content,
                timestamp=timestamp,
                is_self=is_self
            ))

        return messages


class WeChatJSONParser:
    """微信 JSON 格式解析器"""

    def parse(self, json_path: Path) -> List[WeChatMessage]:
        """解析微信 JSON 格式聊天记录"""
        messages = []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("messages", [])
        else:
            return messages

        for item in items:
            if not isinstance(item, dict):
                continue

            msg_type = item.get("type", item.get("msg_type", 1))

            if msg_type != 1:
                continue

            content = item.get("text", item.get("content", item.get("strContent", "")))
            if not content or not isinstance(content, str):
                continue

            sender = item.get("sender", item.get("nickname", item.get("fromName", "Unknown")))
            sender = str(sender) if sender else "Unknown"

            date_str = item.get("date", item.get("timestamp", ""))
            try:
                if isinstance(date_str, str):
                    timestamp = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                else:
                    timestamp = datetime.fromtimestamp(date_str)
            except:
                timestamp = datetime.now()

            is_self = item.get("isSelf", item.get("is_self", False))

            messages.append(WeChatMessage(
                sender=sender,
                content=content,
                timestamp=timestamp,
                msg_type=msg_type,
                is_self=is_self
            ))

        return messages


class WeChatTextParser:
    """微信文本格式解析器（简单文本格式）"""

    def parse(self, text_path: Path) -> List[WeChatMessage]:
        """解析简单的文本格式聊天记录"""
        messages = []

        with open(text_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_sender = None
        current_content = []
        current_time = datetime.now()

        time_pattern = re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}")
        sender_pattern = re.compile(r"^(.+?)\s*[：:]\s*(.+)$")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if time_pattern.match(line):
                if current_sender and current_content:
                    messages.append(WeChatMessage(
                        sender=current_sender,
                        content=" ".join(current_content),
                        timestamp=current_time
                    ))

                try:
                    current_time = datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
                except:
                    current_time = datetime.now()

                current_sender = None
                current_content = []

            elif sender_pattern.match(line):
                if current_sender and current_content:
                    messages.append(WeChatMessage(
                        sender=current_sender,
                        content=" ".join(current_content),
                        timestamp=current_time
                    ))

                match = sender_pattern.match(line)
                current_sender = match.group(1)
                current_content = [match.group(2)]

            elif current_sender:
                current_content.append(line)

        if current_sender and current_content:
            messages.append(WeChatMessage(
                sender=current_sender,
                content=" ".join(current_content),
                timestamp=current_time
            ))

        return messages


class WeChatCSVParser:
    """微信 CSV 格式解析器"""

    def parse(self, csv_path: Path) -> List[WeChatMessage]:
        """解析 CSV 格式聊天记录"""
        messages = []

        try:
            import pandas as pd
        except ImportError:
            print("请安装 pandas: pip install pandas")
            return messages

        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            content = str(row.get("content", row.get("text", row.get("message", ""))))
            if not content or content == "nan":
                continue

            sender = str(row.get("sender", row.get("nickname", row.get("from", "Unknown"))))
            date_str = str(row.get("date", row.get("time", row.get("timestamp", ""))))

            try:
                if "timestamp" in str(df.columns).lower():
                    timestamp = datetime.fromtimestamp(float(date_str))
                else:
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                timestamp = datetime.now()

            messages.append(WeChatMessage(
                sender=sender,
                content=content,
                timestamp=timestamp
            ))

        return messages


def get_wechat_parser(format_type: str):
    """
    根据格式类型获取解析器

    Args:
        format_type: 格式类型 (html, json, text, csv)

    Returns:
        对应的解析器实例
    """
    parsers = {
        "html": WeChatHTMLParser,
        "json": WeChatJSONParser,
        "text": WeChatTextParser,
        "csv": WeChatCSVParser,
    }

    parser_class = parsers.get(format_type.lower())
    if not parser_class:
        raise ValueError(f"不支持的格式：{format_type}")

    return parser_class()
