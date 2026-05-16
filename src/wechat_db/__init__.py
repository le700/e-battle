"""
微信数据库读取模块（简化版）

注意：完整的微信数据库读取需要：
1. 提取数据库密钥（涉及内存扫描、Hook等技术）
2. 解密WCDB数据库（需要原生库支持）
3. 处理微信特有的数据结构

这个模块提供简化版的实现：
1. 通过 WeFlow API 读取
2. 读取导出的数据库文件
3. 解析微信特定格式

对于完整的微信数据库读取，推荐使用 WeFlow 的专业功能。
"""

import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WeChatDBReader:
    """微信数据库读取器（简化版）

    支持：
    - 读取微信导出的数据库文件
    - 解析微信消息格式
    - 处理文本消息

    注意：此模块不包含完整的密钥提取和数据库解密功能
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path
        self.conn = None

    def connect(self, db_path: Path) -> bool:
        """连接到数据库"""
        try:
            self.db_path = db_path
            self.conn = sqlite3.connect(str(db_path))
            logger.info(f"成功连接到数据库: {db_path}")
            return True
        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_messages(self, talker: str, limit: int = 1000) -> List[Dict]:
        """获取指定联系人的消息

        Args:
            talker: 联系人ID
            limit: 返回消息数量限制

        Returns:
            消息列表
        """
        if not self.conn:
            logger.error("未连接到数据库")
            return []

        try:
            cursor = self.conn.cursor()

            # 微信消息表的查询
            # 注意：实际的表结构可能因微信版本而异
            query = """
                SELECT
                    msg.localId,
                    msg.Talker,
                    msg.Type,
                    msg.StrContent,
                    msg.CreateTime,
                    msg.IsSelf
                FROM
                    message msg
                WHERE
                    msg.Talker = ?
                ORDER BY
                    msg.CreateTime DESC
                LIMIT ?
            """

            cursor.execute(query, (talker, limit))
            rows = cursor.fetchall()

            messages = []
            for row in rows:
                local_id, talker, msg_type, content, create_time, is_self = row

                # 转换时间戳
                try:
                    timestamp = datetime.fromtimestamp(create_time / 1000)
                except:
                    timestamp = datetime.now()

                # 过滤非文本消息（Type != 1 表示非文本消息）
                if msg_type != 1:
                    content = f"[类型 {msg_type} 的消息]"

                messages.append({
                    "localId": local_id,
                    "talker": talker,
                    "type": msg_type,
                    "content": content or "",
                    "createTime": create_time,
                    "timestamp": timestamp.isoformat(),
                    "isSelf": bool(is_self),
                    "sender": "我" if is_self else talker
                })

            # 反转列表，按时间正序排列
            messages.reverse()
            return messages

        except sqlite3.OperationalError as e:
            logger.error(f"查询失败，表可能不存在或结构不同: {e}")
            return []
        except Exception as e:
            logger.error(f"获取消息失败: {e}")
            return []

    def get_sessions(self) -> List[Dict]:
        """获取会话列表

        Returns:
            会话列表
        """
        if not self.conn:
            logger.error("未连接到数据库")
            return []

        try:
            cursor = self.conn.cursor()

            # 查询最近的会话
            query = """
                SELECT DISTINCT
                    msg.Talker,
                    MAX(msg.CreateTime) as LastTime,
                    msg.StrContent as LastMessage
                FROM
                    message msg
                WHERE
                    msg.Type = 1
                GROUP BY
                    msg.Talker
                ORDER BY
                    LastTime DESC
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            sessions = []
            for row in rows:
                talker, last_time, last_message = row
                sessions.append({
                    "talker": talker,
                    "lastTime": last_time,
                    "lastMessage": last_message or ""
                })

            return sessions

        except sqlite3.OperationalError as e:
            logger.error(f"查询失败: {e}")
            return []
        except Exception as e:
            logger.error(f"获取会话失败: {e}")
            return []

    def get_contact_info(self, talker: str) -> Optional[Dict]:
        """获取联系人信息

        Args:
            talker: 联系人ID

        Returns:
            联系人信息
        """
        if not self.conn:
            logger.error("未连接到数据库")
            return None

        try:
            cursor = self.conn.cursor()

            # 查询联系人信息
            query = """
                SELECT
                    c.UserName,
                    c.NickName,
                    c.Remark,
                    c.Alias
                FROM
                    Contact c
                WHERE
                    c.UserName = ?
            """

            cursor.execute(query, (talker,))
            row = cursor.fetchone()

            if row:
                return {
                    "userName": row[0],
                    "nickName": row[1],
                    "remark": row[2],
                    "alias": row[3]
                }

            return None

        except sqlite3.OperationalError as e:
            logger.error(f"查询失败: {e}")
            return None
        except Exception as e:
            logger.error(f"获取联系人信息失败: {e}")
            return None


class WeChatFileParser:
    """微信聊天记录文件解析器

    支持解析微信导出的各种格式：
    - JSON 格式
    - HTML 格式（需要 BeautifulSoup）
    - TXT 格式
    - ChatLab 格式
    """

    @staticmethod
    def parse_json(file_path: Path) -> List[Dict]:
        """解析 JSON 格式文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 支持多种 JSON 结构
            if isinstance(data, list):
                messages = data
            elif isinstance(data, dict):
                if "messages" in data:
                    messages = data["messages"]
                elif "chat_history" in data:
                    messages = data["chat_history"]
                else:
                    messages = [data]
            else:
                messages = []

            result = []
            for msg in messages:
                if not isinstance(msg, dict):
                    continue

                # 提取时间
                timestamp = msg.get("timestamp", msg.get("createTime", 0))
                if isinstance(timestamp, str):
                    try:
                        timestamp = int(datetime.fromisoformat(timestamp).timestamp() * 1000)
                    except:
                        timestamp = 0

                result.append({
                    "sender": msg.get("sender", msg.get("from", msg.get("nickname", "Unknown"))),
                    "content": msg.get("content", msg.get("text", "")),
                    "timestamp": timestamp,
                    "type": msg.get("type", 1),
                    "isSelf": msg.get("isSelf", msg.get("is_self", False))
                })

            return result

        except Exception as e:
            logger.error(f"解析 JSON 文件失败: {e}")
            return []

    @staticmethod
    def parse_chatlab(file_path: Path) -> List[Dict]:
        """解析 ChatLab 格式文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            messages = []
            for msg in data.get("messages", []):
                messages.append({
                    "sender": msg.get("accountName", msg.get("sender", "Unknown")),
                    "content": msg.get("content", ""),
                    "timestamp": msg.get("timestamp", 0),
                    "type": msg.get("type", 0),
                    "isSelf": False  # ChatLab格式中不包含此字段
                })

            return messages

        except Exception as e:
            logger.error(f"解析 ChatLab 文件失败: {e}")
            return []

    @staticmethod
    def parse_text(file_path: Path) -> List[Dict]:
        """解析 TXT 格式文件"""
        try:
            import re

            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            messages = []
            time_pattern = re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}")
            sender_pattern = re.compile(r"^(.+?)\s*[：:]\s*(.*)$")

            current_time = datetime.now()
            current_sender = None
            current_content = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if time_pattern.match(line):
                    # 时间行，保存之前消息
                    if current_sender and current_content:
                        messages.append({
                            "sender": current_sender,
                            "content": " ".join(current_content),
                            "timestamp": int(current_time.timestamp() * 1000),
                            "type": 1,
                            "isSelf": False
                        })
                        current_content = []

                    try:
                        current_time = datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
                    except:
                        current_time = datetime.now()

                elif sender_pattern.match(line):
                    # 发送者行
                    if current_sender and current_content:
                        messages.append({
                            "sender": current_sender,
                            "content": " ".join(current_content),
                            "timestamp": int(current_time.timestamp() * 1000),
                            "type": 1,
                            "isSelf": False
                        })
                        current_content = []

                    match = sender_pattern.match(line)
                    current_sender = match.group(1)
                    if match.group(2):
                        current_content.append(match.group(2))

                elif current_sender:
                    current_content.append(line)

            # 保存最后一条消息
            if current_sender and current_content:
                messages.append({
                    "sender": current_sender,
                    "content": " ".join(current_content),
                    "timestamp": int(current_time.timestamp() * 1000),
                    "type": 1,
                    "isSelf": False
                })

            return messages

        except Exception as e:
            logger.error(f"解析 TXT 文件失败: {e}")
            return []

    @staticmethod
    def parse_html(file_path: Path) -> List[Dict]:
        """解析 HTML 格式文件"""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.warning("需要安装 beautifulsoup4 来解析 HTML: pip install beautifulsoup4")
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            messages = []
            time_pattern = re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}")

            # 尝试多种选择器
            chat_items = (
                soup.find_all("div", class_="chat_item") or
                soup.find_all("div", class_="message") or
                soup.find_all("div", class_="bubble")
            )

            for item in chat_items:
                # 提取发送者
                sender_elem = (
                    item.find("span", class_="nickname") or
                    item.find("span", class_="nick_name") or
                    item.find("div", class_="sender")
                )
                sender = sender_elem.text.strip() if sender_elem else "Unknown"

                # 提取内容
                content_elem = (
                    item.find("div", class_="content") or
                    item.find("p", class_="text") or
                    item.find("span", class_="content")
                )
                content = content_elem.text.strip() if content_elem else ""

                # 提取时间
                time_elem = item.find("span", class_="time")
                timestamp = int(datetime.now().timestamp() * 1000)
                if time_elem:
                    time_str = time_elem.text.strip()
                    try:
                        if time_pattern.match(time_str):
                            timestamp = int(datetime.strptime(
                                time_str, "%Y-%m-%d %H:%M"
                            ).timestamp() * 1000)
                    except:
                        pass

                if content:
                    messages.append({
                        "sender": sender,
                        "content": content,
                        "timestamp": timestamp,
                        "type": 1,
                        "isSelf": False
                    })

            return messages

        except Exception as e:
            logger.error(f"解析 HTML 文件失败: {e}")
            return []

    @classmethod
    def parse_file(cls, file_path: Path) -> List[Dict]:
        """根据文件类型自动选择解析方法"""
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return []

        suffix = file_path.suffix.lower()

        parsers = {
            ".json": cls.parse_json,
            ".txt": cls.parse_text,
            ".html": cls.parse_html,
        }

        # 检查是否是 ChatLab 格式
        if suffix == ".json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "chatlab" in data:
                        return cls.parse_chatlab(file_path)
            except:
                pass

        parser = parsers.get(suffix)
        if parser:
            return parser(file_path)

        logger.warning(f"不支持的文件格式: {suffix}")
        return []


def read_wechat_export(
    file_path: Path,
    talker: Optional[str] = None
) -> List[Dict]:
    """读取微信导出的聊天记录

    Args:
        file_path: 文件路径
        talker: 过滤特定联系人的消息（可选）

    Returns:
        消息列表
    """
    messages = WeChatFileParser.parse_file(file_path)

    if talker:
        messages = [m for m in messages if m.get("sender") == talker]

    return messages
