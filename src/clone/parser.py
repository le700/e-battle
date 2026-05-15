"""
ChatParser - 聊天记录解析器

支持 Telegram、微信、QQ 等平台的聊天记录解析
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatMessage:
    """单条聊天消息"""
    sender: str
    content: str
    timestamp: datetime
    reply_to: Optional[str] = None


class ChatParser:
    """聊天记录解析器基类"""

    def parse(self, path: Path) -> List[ChatMessage]:
        """解析聊天记录"""
        raise NotImplementedError


class TelegramChatParser(ChatParser):
    """Telegram 聊天记录解析器"""

    def parse(self, path: Path) -> List[ChatMessage]:
        """
        解析 Telegram 导出的 JSON 格式聊天记录

        Args:
            path: Telegram 导出的聊天记录文件夹路径

        Returns:
            聊天消息列表
        """
        messages = []
        result_json_path = path / "result.json"

        if not result_json_path.exists():
            raise FileNotFoundError(f"找不到聊天记录文件: {result_json_path}")

        with open(result_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        messages_data = data.get("messages", [])

        for msg in messages_data:
            if msg.get("type") != "message":
                continue

            text = msg.get("text", "")
            if not text or not isinstance(text, str):
                continue

            sender = msg.get("from", "Unknown")
            date_str = msg.get("date", "")

            try:
                timestamp = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except:
                timestamp = datetime.now()

            messages.append(ChatMessage(
                sender=sender,
                content=text.strip(),
                timestamp=timestamp
            ))

        return messages

    def extract_conversations(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """
        将聊天记录转换为对话格式

        Args:
            messages: 聊天消息列表

        Returns:
            对话列表，每项包含 question 和 answer
        """
        conversations = []
        current_q = None
        last_sender = None

        for msg in messages:
            if last_sender and last_sender != msg.sender:
                if current_q:
                    conversations.append({
                        "question": current_q,
                        "answer": msg.content
                    })
                current_q = msg.content
            elif not current_q:
                current_q = msg.content

            last_sender = msg.sender

        return conversations


class WeChatChatParser(ChatParser):
    """微信聊天记录解析器"""

    def parse(self, path: Path) -> List[ChatMessage]:
        """
        解析微信导出的聊天记录

        支持格式：
        - HTML 格式（微信桌面版导出）
        - JSON 格式（第三方工具导出）
        - TXT 格式（简单文本格式）

        Args:
            path: 微信聊天记录文件路径或文件夹

        Returns:
            聊天消息列表
        """
        path = Path(path)

        if path.is_file():
            if path.suffix == ".html":
                return self._parse_html(path)
            elif path.suffix == ".json":
                return self._parse_json(path)
            elif path.suffix == ".txt":
                return self._parse_text(path)
            else:
                raise ValueError(f"不支持的文件格式: {path.suffix}")
        elif path.is_dir():
            html_files = list(path.glob("*.html"))
            if html_files:
                return self._parse_html(html_files[0])
            json_files = list(path.glob("*.json"))
            if json_files:
                return self._parse_json(json_files[0])
            raise FileNotFoundError(f"目录中没有找到支持的聊天记录文件: {path}")

    def _parse_html(self, html_path: Path) -> List[ChatMessage]:
        """解析 HTML 格式"""
        messages = []

        try:
            from bs4 import BeautifulSoup
        except ImportError:
            print("提示: 安装 beautifulsoup4 可以解析 HTML 格式")
            print("运行: pip install beautifulsoup4")
            return messages

        with open(html_path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        chat_items = soup.find_all("div", class_="chat_item")

        if not chat_items:
            bubble_divs = soup.find_all("div", class_="bubble")
            for div in bubble_divs:
                content_elem = div.find("div", class_="content")
                if content_elem:
                    sender_elem = div.find("span", class_="nickname")
                    time_elem = div.find("span", class_="time")

                    sender = sender_elem.text.strip() if sender_elem else "Unknown"
                    content = content_elem.text.strip()
                    try:
                        timestamp = datetime.strptime(
                            time_elem.text.strip(), "%Y-%m-%d %H:%M:%S"
                        ) if time_elem else datetime.now()
                    except:
                        timestamp = datetime.now()

                    messages.append(ChatMessage(
                        sender=sender,
                        content=content,
                        timestamp=timestamp
                    ))
        else:
            for item in chat_items:
                sender_elem = item.find("span", class_="nick_name")
                content_elem = item.find("div", class_="text")
                time_elem = item.find("span", class_="time")

                if not content_elem:
                    continue

                sender = sender_elem.text.strip() if sender_elem else "Unknown"
                content = content_elem.text.strip()

                try:
                    timestamp = datetime.strptime(
                        time_elem.text.strip(), "%Y-%m-%d %H:%M:%S"
                    ) if time_elem else datetime.now()
                except:
                    timestamp = datetime.now()

                messages.append(ChatMessage(
                    sender=sender,
                    content=content,
                    timestamp=timestamp
                ))

        return messages

    def _parse_json(self, json_path: Path) -> List[ChatMessage]:
        """解析 JSON 格式"""
        messages = []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("messages", data.get("chat_history", []))
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

            messages.append(ChatMessage(
                sender=sender,
                content=content,
                timestamp=timestamp
            ))

        return messages

    def _parse_text(self, text_path: Path) -> List[ChatMessage]:
        """解析纯文本格式"""
        messages = []

        with open(text_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_sender = None
        current_content = []
        current_time = datetime.now()

        time_pattern = re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}")
        sender_pattern = re.compile(r"^(.+?)\s*[：:]\s*(.*)$")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if time_pattern.match(line):
                if current_sender and current_content:
                    messages.append(ChatMessage(
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
                    messages.append(ChatMessage(
                        sender=current_sender,
                        content=" ".join(current_content),
                        timestamp=current_time
                    ))

                match = sender_pattern.match(line)
                current_sender = match.group(1)
                current_content = [match.group(2)] if match.group(2) else []

            elif current_sender:
                current_content.append(line)

        if current_sender and current_content:
            messages.append(ChatMessage(
                sender=current_sender,
                content=" ".join(current_content),
                timestamp=current_time
            ))

        return messages

    def extract_conversations(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """将聊天记录转换为对话格式"""
        conversations = []
        last_sender = None

        for msg in messages:
            if last_sender and last_sender != msg.sender:
                conversations.append({
                    "question": msg.content,
                    "answer": ""
                })
            elif conversations:
                if conversations[-1]["answer"] == "":
                    conversations[-1]["answer"] = msg.content
                else:
                    conversations.append({
                        "question": msg.content,
                        "answer": ""
                    })

            last_sender = msg.sender

        return [c for c in conversations if c["answer"]]


class QQChatParser(ChatParser):
    """QQ 聊天记录解析器（预留接口）"""

    def parse(self, path: Path) -> List[ChatMessage]:
        """解析 QQ 导出的聊天记录"""
        messages = []

        try:
            from bs4 import BeautifulSoup
        except ImportError:
            return messages

        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")

        messages_div = soup.find_all("div", class_="message")

        for div in messages_div:
            sender_elem = div.find("span", class_="sender")
            content_elem = div.find("div", class_="content")

            if not content_elem:
                continue

            sender = sender_elem.text.strip() if sender_elem else "Unknown"
            content = content_elem.text.strip()

            messages.append(ChatMessage(
                sender=sender,
                content=content,
                timestamp=datetime.now()
            ))

        return messages


def get_parser(platform: str) -> ChatParser:
    """
    根据平台名称获取对应的解析器

    Args:
        platform: 平台名称 (telegram, wechat, qq)

    Returns:
        对应的解析器实例
    """
    parsers = {
        "telegram": TelegramChatParser,
        "wechat": WeChatChatParser,
        "weixin": WeChatChatParser,
        "qq": QQChatParser,
    }

    platform_lower = platform.lower()
    for key in parsers.keys():
        if key in platform_lower:
            return parsers[key]()

    raise ValueError(f"不支持的平台: {platform}。支持的平台: telegram, wechat, qq")
