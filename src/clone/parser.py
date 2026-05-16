"""
ChatParser - 聊天记录解析器

支持 Telegram、微信、QQ 等平台的聊天记录解析
智能检测聊天记录格式，支持多种导出方式
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """单条聊天消息"""
    sender: str
    content: str
    timestamp: datetime
    reply_to: Optional[str] = None
    platform: Optional[str] = None


@dataclass
class ParseResult:
    """解析结果"""
    messages: List[ChatMessage]
    format_detected: str
    platform_detected: str
    message_count: int
    participants: List[str]


class ChatParser:
    """聊天记录解析器基类"""

    def parse(self, path: Path) -> List[ChatMessage]:
        """解析聊天记录"""
        raise NotImplementedError
    
    def can_parse(self, path: Path) -> Tuple[bool, float]:
        """
        检查是否能解析该文件
        
        Returns:
            (是否能解析, 置信度 0-1)
        """
        return False, 0.0


class TelegramChatParser(ChatParser):
    """Telegram 聊天记录解析器"""
    
    def can_parse(self, path: Path) -> Tuple[bool, float]:
        """检查是否能解析"""
        if path.is_dir():
            result_json = path / "result.json"
            if result_json.exists():
                return True, 0.9
        elif path.is_file() and path.suffix == ".json":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "messages" in data or isinstance(data, list):
                        return True, 0.8
            except:
                pass
        return False, 0.0

    def parse(self, path: Path) -> List[ChatMessage]:
        """
        解析 Telegram 导出的 JSON 格式聊天记录

        Args:
            path: Telegram 导出的聊天记录文件夹路径

        Returns:
            聊天消息列表
        """
        messages = []
        result_json_path = None
        
        if path.is_dir():
            result_json_path = path / "result.json"
        elif path.is_file() and path.suffix == ".json":
            result_json_path = path
        
        if not result_json_path or not result_json_path.exists():
            raise FileNotFoundError(f"找不到聊天记录文件: {result_json_path}")

        with open(result_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        messages_data = []
        if isinstance(data, list):
            messages_data = data
        elif isinstance(data, dict):
            messages_data = data.get("messages", [])

        for msg in messages_data:
            if msg.get("type") != "message":
                continue

            text = msg.get("text", "")
            if not text:
                continue
            
            if isinstance(text, list):
                text_parts = []
                for part in text:
                    if isinstance(part, str):
                        text_parts.append(part)
                    elif isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                text = " ".join(text_parts)
            
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
                timestamp=timestamp,
                platform="telegram"
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
    """微信聊天记录解析器 - 支持多种微信导出格式"""
    
    def can_parse(self, path: Path) -> Tuple[bool, float]:
        """
        智能检测是否为微信聊天记录
        
        Returns:
            (是否能解析, 置信度 0-1)
        """
        if not path.exists():
            return False, 0.0
        
        confidence = 0.0
        
        if path.is_file():
            try:
                # 检查文件内容特征
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(10000)  # 只读取前10KB
                    
                    # HTML格式特征
                    if path.suffix == ".html":
                        if "微信" in content or "WeChat" in content or "chat_item" in content:
                            return True, 0.9
                        if "nickname" in content and "time" in content:
                            return True, 0.8
                    
                    # JSON格式特征
                    if path.suffix == ".json":
                        if "sender" in content or "nickname" in content or "content" in content:
                            return True, 0.85
                        if "微信" in content or "wechat" in content.lower():
                            return True, 0.8
                    
                    # TXT格式特征
                    if path.suffix == ".txt":
                        # 检查时间格式
                        if re.search(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", content):
                            confidence += 0.3
                        # 检查微信常见用户名格式
                        if re.search(r"^[^\n]+[：:]", content, re.MULTILINE):
                            confidence += 0.3
                        if "微信" in content or "WeChat" in content:
                            confidence += 0.3
                        if confidence > 0.3:
                            return True, confidence
                    
                    # CSV格式
                    if path.suffix == ".csv":
                        return True, 0.7
            except:
                pass
        
        elif path.is_dir():
            # 检查目录中的文件
            for ext in [".html", ".txt", ".json", ".csv"]:
                files = list(path.glob(f"*{ext}"))
                if files:
                    # 检查第一个文件
                    return self.can_parse(files[0])
        
        return False, 0.0

    def parse(self, path: Path) -> List[ChatMessage]:
        """
        解析微信导出的聊天记录 - 智能识别格式

        支持格式：
        - HTML 格式（微信桌面版导出）
        - JSON 格式（第三方工具导出）
        - TXT 格式（多种变体）
        - CSV 格式
        - 微信Mac版导出格式
        - 微信iOS/Android导出格式

        Args:
            path: 微信聊天记录文件路径或文件夹

        Returns:
            聊天消息列表
        """
        path = Path(path)
        
        if path.is_dir():
            # 目录模式，查找支持的文件
            parsers = [
                (".html", self._parse_html),
                (".json", self._parse_json),
                (".txt", self._parse_text),
                (".csv", self._parse_csv),
            ]
            for ext, parser_func in parsers:
                files = list(path.glob(f"*{ext}"))
                if files:
                    logger.info(f"检测到 {ext} 格式，尝试解析: {files[0]}")
                    return parser_func(files[0])
            raise FileNotFoundError(f"目录中没有找到支持的聊天记录文件: {path}")
        
        elif path.is_file():
            suffix = path.suffix.lower()
            
            if suffix == ".html":
                return self._parse_html(path)
            elif suffix == ".json":
                return self._parse_json(path)
            elif suffix == ".txt":
                return self._parse_text(path)
            elif suffix == ".csv":
                return self._parse_csv(path)
            else:
                # 尝试所有解析器
                logger.warning(f"未知后缀 {suffix}，尝试所有解析器...")
                parsers = [
                    self._parse_text,
                    self._parse_json,
                    self._parse_html,
                    self._parse_csv,
                ]
                for parser_func in parsers:
                    try:
                        result = parser_func(path)
                        if result:
                            logger.info(f"使用 {parser_func.__name__} 成功解析")
                            return result
                    except:
                        continue
                raise ValueError(f"无法解析文件: {path}")
        
        raise FileNotFoundError(f"路径不存在: {path}")
    
    def _parse_csv(self, csv_path: Path) -> List[ChatMessage]:
        """解析 CSV 格式"""
        messages = []
        try:
            import csv
        except ImportError:
            logger.warning("csv 模块不可用，跳过 CSV 解析")
            return messages
        
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                
                # 尝试多种列名映射
                field_mappings = [
                    {"sender": ["sender", "nickname", "from", "用户", "发送者"],
                     "content": ["content", "text", "message", "内容", "消息"],
                     "time": ["time", "date", "timestamp", "时间", "日期"]}
                ]
                
                # 检测最佳字段映射
                headers = reader.fieldnames or []
                best_map = None
                best_score = 0
                
                for mapping in field_mappings:
                    score = 0
                    for _, possible_names in mapping.items():
                        for name in possible_names:
                            if name in headers:
                                score += 1
                    if score > best_score:
                        best_score = score
                        best_map = mapping
                
                if best_map:
                    # 使用找到的最佳映射
                    for row in reader:
                        sender = self._extract_field(row, best_map["sender"], "Unknown")
                        content = self._extract_field(row, best_map["content"], "")
                        time_str = self._extract_field(row, best_map["time"], "")
                        
                        if not content:
                            continue
                        
                        try:
                            timestamp = self._parse_time(time_str)
                        except:
                            timestamp = datetime.now()
                        
                        messages.append(ChatMessage(
                            sender=sender,
                            content=content.strip(),
                            timestamp=timestamp,
                            platform="wechat"
                        ))
        except Exception as e:
            logger.warning(f"CSV 解析失败: {e}")
        
        return messages
    
    def _extract_field(self, row: Dict, possible_names: List[str], default: str) -> str:
        """从字典中提取字段，尝试多个可能的键名"""
        for name in possible_names:
            if name in row:
                return str(row[name])
        return default
    
    def _parse_time(self, time_str: str) -> datetime:
        """解析多种时间格式"""
        if not time_str:
            return datetime.now()
        
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M",
            "%Y年%m月%d日 %H:%M:%S",
            "%Y年%m月%d日 %H:%M",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str.strip(), fmt)
            except:
                continue
        
        # 尝试时间戳
        try:
            if str(time_str).isdigit():
                ts = int(time_str)
                if ts > 10000000000:  # 毫秒
                    ts = ts // 1000
                return datetime.fromtimestamp(ts)
        except:
            pass
        
        return datetime.now()

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

        # 尝试多种常见的微信HTML结构
        chat_selectors = [
            ("div", "chat_item"),
            ("div", "bubble"),
            ("div", "message"),
            ("div", "msg"),
        ]
        
        for tag, class_name in chat_selectors:
            chat_items = soup.find_all(tag, class_=class_name)
            if chat_items:
                logger.info(f"使用选择器 {tag}.{class_name} 找到 {len(chat_items)} 条消息")
                for item in chat_items:
                    # 尝试多种方式提取发送者
                    sender_selectors = [
                        ("span", "nickname"),
                        ("span", "nick_name"),
                        ("span", "sender"),
                        ("div", "nickname"),
                    ]
                    
                    sender = "Unknown"
                    for s_tag, s_class in sender_selectors:
                        sender_elem = item.find(s_tag, class_=s_class)
                        if sender_elem:
                            sender = sender_elem.text.strip()
                            break
                    
                    # 尝试多种方式提取内容
                    content_selectors = [
                        ("div", "content"),
                        ("div", "text"),
                        ("p", None),
                        ("span", "text"),
                    ]
                    
                    content = ""
                    for c_tag, c_class in sender_selectors:
                        content_elem = item.find(c_tag, class_=c_class)
                        if content_elem:
                            content = content_elem.text.strip()
                            break
                    
                    # 如果都没找到，直接获取item的文本
                    if not content:
                        content = item.text.strip()
                    
                    if not content:
                        continue
                    
                    # 提取时间
                    time_selectors = [
                        ("span", "time"),
                        ("div", "time"),
                    ]
                    
                    timestamp = datetime.now()
                    for t_tag, t_class in time_selectors:
                        time_elem = item.find(t_tag, class_=t_class)
                        if time_elem:
                            try:
                                timestamp = self._parse_time(time_elem.text.strip())
                                break
                            except:
                                continue
                    
                    messages.append(ChatMessage(
                        sender=sender,
                        content=content,
                        timestamp=timestamp,
                        platform="wechat"
                    ))
                
                if messages:
                    break
        
        return messages

    def _parse_json(self, json_path: Path) -> List[ChatMessage]:
        """解析 JSON 格式 - 支持更多JSON结构"""
        messages = []

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 支持多种JSON结构
        messages_data = []
        if isinstance(data, list):
            messages_data = data
        elif isinstance(data, dict):
            # 尝试多种可能的键名
            possible_keys = ["messages", "chat_history", "chats", "data", "list", "records"]
            for key in possible_keys:
                if key in data and isinstance(data[key], list):
                    messages_data = data[key]
                    break
            
            # 如果还没找到，检查是否直接是消息数组的包装
            if not messages_data and len(data) > 0 and isinstance(list(data.values())[0], list):
                messages_data = list(data.values())[0]

        for item in messages_data:
            if not isinstance(item, dict):
                continue

            # 跳过非文本消息
            msg_type = item.get("type", item.get("msg_type", 1))
            if msg_type not in [1, "text", "message"] and isinstance(msg_type, (int, str)):
                continue

            # 提取内容
            content_keys = ["text", "content", "strContent", "message", "msg"]
            content = ""
            for key in content_keys:
                if key in item:
                    content = item[key]
                    if content:
                        break
            
            if not content or not isinstance(content, str):
                continue

            # 提取发送者
            sender_keys = ["sender", "nickname", "fromName", "from", "user", "speaker"]
            sender = "Unknown"
            for key in sender_keys:
                if key in item:
                    sender = str(item[key])
                    if sender:
                        break

            # 提取时间
            date_keys = ["date", "timestamp", "time", "createTime", "create_time"]
            date_str = ""
            for key in date_keys:
                if key in item:
                    date_str = item[key]
                    if date_str:
                        break
            
            try:
                timestamp = self._parse_time(str(date_str))
            except:
                timestamp = datetime.now()

            messages.append(ChatMessage(
                sender=sender,
                content=content,
                timestamp=timestamp,
                platform="wechat"
            ))

        return messages

    def _parse_text(self, text_path: Path) -> List[ChatMessage]:
        """解析纯文本格式 - 支持更多变体"""
        messages = []

        with open(text_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_sender = None
        current_content = []
        current_time = datetime.now()

        # 多种时间格式正则
        time_patterns = [
            re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}"),  # 2024-01-01 12:00:00
            re.compile(r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}"),  # 2024/01/01 12:00:00
            re.compile(r"\d{4}年\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{2}:\d{2}"),  # 2024年1月1日 12:00:00
            re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}"),  # 2024-01-01 12:00
            re.compile(r"\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}"),  # 2024/01/01 12:00
        ]
        
        # 多种发送者格式正则
        sender_patterns = [
            re.compile(r"^(.+?)\s*[：:]\s*(.*)$"),  # 用户名: 内容
            re.compile(r"^<(.+?)>\s*(.*)$"),  # <用户名> 内容
            re.compile(r"^\[(.+?)\]\s*(.*)$"),  # [用户名] 内容
            re.compile(r"^【(.+?)】\s*(.*)$"),  # 【用户名】内容
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是时间行
            is_time_line = False
            for pattern in time_patterns:
                if pattern.match(line):
                    # 保存之前的消息
                    if current_sender and current_content:
                        messages.append(ChatMessage(
                            sender=current_sender,
                            content=" ".join(current_content),
                            timestamp=current_time,
                            platform="wechat"
                        ))
                    
                    # 解析新时间
                    try:
                        current_time = self._parse_time(line)
                    except:
                        current_time = datetime.now()
                    
                    current_sender = None
                    current_content = []
                    is_time_line = True
                    break
            
            if is_time_line:
                continue

            # 检查是否是新发送者行
            is_sender_line = False
            for pattern in sender_patterns:
                match = pattern.match(line)
                if match:
                    # 保存之前的消息
                    if current_sender and current_content:
                        messages.append(ChatMessage(
                            sender=current_sender,
                            content=" ".join(current_content),
                            timestamp=current_time,
                            platform="wechat"
                        ))
                    
                    current_sender = match.group(1).strip()
                    content_part = match.group(2).strip()
                    current_content = [content_part] if content_part else []
                    is_sender_line = True
                    break
            
            if is_sender_line:
                continue

            # 如果是现有发送者的内容延续
            if current_sender:
                current_content.append(line)

        # 保存最后一条消息
        if current_sender and current_content:
            messages.append(ChatMessage(
                sender=current_sender,
                content=" ".join(current_content),
                timestamp=current_time,
                platform="wechat"
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
        platform: 平台名称 (telegram, wechat, qq, txt, json)

    Returns:
        对应的解析器实例
    """
    parsers = {
        "telegram": TelegramChatParser,
        "wechat": WeChatChatParser,
        "weixin": WeChatChatParser,
        "qq": QQChatParser,
        "txt": GenericTextParser,
        "text": GenericTextParser,
        "json": GenericJSONParser,
    }

    platform_lower = platform.lower()
    
    # 精确匹配
    if platform_lower in parsers:
        return parsers[platform_lower]()
    
    # 部分匹配
    for key in parsers.keys():
        if key in platform_lower:
            return parsers[key]()

    raise ValueError(f"不支持的平台: {platform}。支持的平台: telegram, wechat, qq, txt, json")


class GenericTextParser(ChatParser):
    """通用文本格式解析器 - 解析标准TXT格式聊天记录"""
    
    def can_parse(self, path: Path) -> Tuple[bool, float]:
        """检查是否能解析"""
        if not path.is_file():
            return False, 0.0
        if path.suffix.lower() in [".txt", ".text"]:
            return True, 0.8
        return False, 0.0
    
    def parse(self, path: Path) -> List[ChatMessage]:
        """
        解析通用文本格式聊天记录
        
        支持格式:
        2024-01-01 10:00:00
        用户1: 消息内容
        用户2: 消息内容
        """
        messages = []
        
        time_pattern = re.compile(r"(\d{4}[-/]\d{2}[-/]\d{2}[\s]\d{2}:\d{2}:\d{2})")
        sender_pattern = re.compile(r"^([^:：]+)[:：]\s*(.+)")
        
        current_time = datetime.now()
        current_sender = None
        current_content = []
        
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # 检查是否是时间行
                time_match = time_pattern.search(line)
                if time_match:
                    try:
                        time_str = time_match.group(1).replace("/", "-")
                        current_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        current_time = datetime.now()
                    continue
                
                # 检查是否是发送者行
                sender_match = sender_pattern.match(line)
                if sender_match:
                    # 保存之前的消息
                    if current_sender and current_content:
                        messages.append(ChatMessage(
                            sender=current_sender,
                            content=" ".join(current_content),
                            timestamp=current_time,
                            platform="txt"
                        ))
                    
                    current_sender = sender_match.group(1).strip()
                    current_content = [sender_match.group(2).strip()]
                elif current_sender:
                    # 内容延续
                    current_content.append(line)
        
        # 保存最后一条消息
        if current_sender and current_content:
            messages.append(ChatMessage(
                sender=current_sender,
                content=" ".join(current_content),
                timestamp=current_time,
                platform="txt"
            ))
        
        return messages


class GenericJSONParser(ChatParser):
    """通用JSON格式解析器"""
    
    def can_parse(self, path: Path) -> Tuple[bool, float]:
        """检查是否能解析"""
        if not path.is_file():
            return False, 0.0
        if path.suffix.lower() == ".json":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "messages" in data:
                        return True, 0.9
                    if isinstance(data, list):
                        return True, 0.85
            except:
                pass
        return False, 0.0
    
    def parse(self, path: Path) -> List[ChatMessage]:
        """解析通用JSON格式聊天记录"""
        messages = []
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 处理不同的JSON格式
        messages_data = data.get("messages", data) if isinstance(data, dict) else data
        
        for msg_data in messages_data:
            if isinstance(msg_data, dict):
                sender = msg_data.get("sender", msg_data.get("user", msg_data.get("name", "Unknown")))
                content = msg_data.get("content", msg_data.get("text", msg_data.get("message", "")))
                timestamp_str = msg_data.get("timestamp", msg_data.get("time", msg_data.get("date", "")))
                
                # 解析时间戳
                try:
                    if isinstance(timestamp_str, (int, float)):
                        timestamp = datetime.fromtimestamp(timestamp_str)
                    else:
                        timestamp = datetime.strptime(str(timestamp_str), "%Y-%m-%d %H:%M:%S")
                except:
                    timestamp = datetime.now()
                
                messages.append(ChatMessage(
                    sender=str(sender),
                    content=str(content),
                    timestamp=timestamp,
                    platform="json"
                ))
        
        return messages


def smart_parse_chat(path: Path) -> ParseResult:
    """
    智能解析聊天记录 - 自动检测格式和平台
    
    Args:
        path: 聊天记录文件或目录路径
    
    Returns:
        ParseResult - 解析结果
    """
    path = Path(path)
    
    # 所有可用的解析器
    all_parsers = [
        WeChatChatParser(),
        TelegramChatParser(),
        QQChatParser(),
    ]
    
    best_parser = None
    best_confidence = 0.0
    
    # 找出最佳匹配的解析器
    for parser in all_parsers:
        can_parse, confidence = parser.can_parse(path)
        if can_parse and confidence > best_confidence:
            best_confidence = confidence
            best_parser = parser
    
    if best_parser is None:
        # 尝试通用解析
        logger.warning("无法自动识别格式，尝试使用微信解析器")
        best_parser = WeChatChatParser()
    
    logger.info(f"使用解析器: {best_parser.__class__.__name__}, 置信度: {best_confidence:.2f}")
    
    # 解析消息
    messages = best_parser.parse(path)
    
    # 提取参与者
    participants = list(set(msg.sender for msg in messages))
    participants = [p for p in participants if p and p != "Unknown"]
    
    return ParseResult(
        messages=messages,
        format_detected=best_parser.__class__.__name__,
        platform_detected=getattr(best_parser, 'platform', 'unknown'),
        message_count=len(messages),
        participants=participants
    )
