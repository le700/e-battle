"""
导出模块 - 支持多种格式的聊天记录导出

参考 WeFlow 的设计，支持以下格式：
- ChatLab (行业标准格式)
- HTML (可阅读网页)
- JSON (原始数据)
- TXT (纯文本)
- Excel (表格)
- Markdown
- WeClone兼容格式
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChatLabHeader:
    """ChatLab 格式头部信息"""
    version: str = "0.0.2"
    exportedAt: int = 0
    generator: str = "FriendBattle"
    description: str = "Exported from FriendBattle AI Friend Debate"


@dataclass
class ChatLabMeta:
    """ChatLab 格式元数据"""
    name: str
    platform: str = "wechat"
    type: str = "private"  # private 或 group
    groupId: Optional[str] = None
    groupAvatar: Optional[str] = None


@dataclass
class ChatLabMember:
    """ChatLab 格式成员信息"""
    platformId: str
    accountName: str
    groupNickname: Optional[str] = None
    avatar: Optional[str] = None


@dataclass
class ChatLabMessage:
    """ChatLab 格式消息"""
    sender: str
    accountName: str
    groupNickname: Optional[str] = None
    timestamp: int = 0
    type: int = 0  # 0=文本, 1=图片, 2=语音, 3=视频, 4=文件, 5=表情, 7=链接, 8=位置, 20=红包, 21=转账, 23=通话, 80=系统消息
    content: Optional[str] = None
    platformMessageId: Optional[str] = None
    replyToMessageId: Optional[str] = None


@dataclass
class ChatLabExport:
    """完整的 ChatLab 导出格式"""
    chatlab: ChatLabHeader
    meta: ChatLabMeta
    members: List[ChatLabMember]
    messages: List[ChatLabMessage]


class Exporter:
    """导出器基类"""

    def __init__(self, name: str):
        self.name = name

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """导出聊天记录"""
        raise NotImplementedError

    def get_file_extension(self) -> str:
        """获取文件扩展名"""
        raise NotImplementedError


class ChatLabExporter(Exporter):
    """ChatLab 格式导出器 - 行业标准格式"""

    def __init__(self):
        super().__init__("ChatLab")

    def get_file_extension(self) -> str:
        return ".chatlab.json"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """
        导出为 ChatLab 格式

        ChatLab 是一个标准化的聊天记录交换格式，方便在不同应用间共享数据。
        """
        try:
            # 提取参与者
            participants = set()
            for msg in messages:
                if msg.get("sender"):
                    participants.add(msg["sender"])

            # 构建 ChatLab 结构
            chatlab_header = ChatLabHeader(
                version="0.0.2",
                exportedAt=int(datetime.now().timestamp() * 1000),
                generator="FriendBattle",
                description="Exported from FriendBattle AI Friend Debate"
            )

            meta = ChatLabMeta(
                name=kwargs.get("chat_name", "Unknown Chat"),
                platform="wechat",
                type=kwargs.get("chat_type", "private")
            )

            members = [
                ChatLabMember(platformId=name, accountName=name)
                for name in participants
            ]

            chatlab_messages = []
            for msg in messages:
                timestamp = msg.get("timestamp")
                if isinstance(timestamp, datetime):
                    timestamp = int(timestamp.timestamp() * 1000)
                elif isinstance(timestamp, str):
                    try:
                        timestamp = int(datetime.fromisoformat(timestamp).timestamp() * 1000)
                    except:
                        timestamp = int(datetime.now().timestamp() * 1000)

                chatlab_msg = ChatLabMessage(
                    sender=msg.get("sender", "Unknown"),
                    accountName=msg.get("sender", "Unknown"),
                    timestamp=timestamp,
                    type=self._content_type_to_chatlab_type(msg.get("type", 0)),
                    content=msg.get("content", ""),
                    platformMessageId=msg.get("id"),
                    replyToMessageId=msg.get("reply_to")
                )
                chatlab_messages.append(chatlab_msg)

            export_data = ChatLabExport(
                chatlab=chatlab_header,
                meta=meta,
                members=members,
                messages=chatlab_messages
            )

            # 转换为字典并保存
            export_dict = {
                "chatlab": asdict(export_data.chatlab),
                "meta": asdict(export_data.meta),
                "members": [asdict(m) for m in export_data.members],
                "messages": [asdict(m) for m in export_data.messages]
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_dict, f, ensure_ascii=False, indent=2)

            logger.info(f"ChatLab 导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"ChatLab 导出失败: {e}")
            return False

    def _content_type_to_chatlab_type(self, msg_type: Any) -> int:
        """将内容类型转换为 ChatLab 标准类型"""
        type_map = {
            0: 0,   # 文本
            1: 1,   # 图片
            2: 2,   # 语音
            3: 3,   # 视频
            4: 4,   # 文件
            5: 5,   # 表情
            7: 7,   # 链接
            8: 8,   # 位置
            20: 20, # 红包
            21: 21, # 转账
            23: 23, # 通话
            80: 80, # 系统消息
        }
        return type_map.get(int(msg_type), 0)


class HTMLExporter(Exporter):
    """HTML 格式导出器"""

    def __init__(self):
        super().__init__("HTML")

    def get_file_extension(self) -> str:
        return ".html"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """导出为 HTML 格式"""
        try:
            chat_name = kwargs.get("chat_name", "聊天记录")
            theme = kwargs.get("theme", "light")

            html_content = self._generate_html(chat_name, messages, theme)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"HTML 导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"HTML 导出失败: {e}")
            return False

    def _generate_html(self, chat_name: str, messages: List[Dict], theme: str) -> str:
        """生成 HTML 内容"""
        bg_color = "#f5f5f5" if theme == "light" else "#1a1a1a"
        text_color = "#333" if theme == "light" else "#eee"
        card_bg = "#fff" if theme == "light" else "#2d2d2d"

        messages_html = ""
        for msg in messages:
            sender = msg.get("sender", "未知")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp")

            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime("%Y-%m-%d %H:%M")
            elif isinstance(timestamp, str):
                try:
                    time_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
                except:
                    time_str = timestamp
            else:
                time_str = str(timestamp) if timestamp else ""

            is_self = sender == "我" or sender == "Me"

            bubble_class = "message-self" if is_self else "message-other"
            alignment = "flex-end" if is_self else "flex-start"

            messages_html += f"""
            <div class="message {bubble_class}" style="display: flex; justify-content: {alignment}; margin: 8px 0;">
                <div style="max-width: 70%; background: {card_bg}; padding: 10px 15px; border-radius: 10px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    <div style="font-size: 0.85em; color: #888; margin-bottom: 4px;">{sender}</div>
                    <div style="color: {text_color};">{content}</div>
                    <div style="font-size: 0.75em; color: #aaa; margin-top: 4px; text-align: right;">{time_str}</div>
                </div>
            </div>
            """

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{chat_name} - 聊天记录</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: {bg_color}; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .header {{ text-align: center; padding: 20px; background: {card_bg}; border-radius: 10px; margin-bottom: 20px; }}
        .header h1 {{ color: {text_color}; font-size: 1.5em; }}
        .chat-container {{ background: {card_bg}; border-radius: 10px; padding: 15px; min-height: 500px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 {chat_name}</h1>
            <p style="color: {text_color}; margin-top: 10px; opacity: 0.7;">由 FriendBattle 导出</p>
        </div>
        <div class="chat-container">
            {messages_html}
        </div>
    </div>
</body>
</html>"""


class JSONExporter(Exporter):
    """JSON 格式导出器"""

    def __init__(self):
        super().__init__("JSON")

    def get_file_extension(self) -> str:
        return ".json"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """导出为 JSON 格式"""
        try:
            export_data = {
                "chat_name": kwargs.get("chat_name", "Unknown Chat"),
                "exported_at": datetime.now().isoformat(),
                "generator": "FriendBattle",
                "message_count": len(messages),
                "messages": messages
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            logger.info(f"JSON 导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"JSON 导出失败: {e}")
            return False


class TXTExporter(Exporter):
    """TXT 格式导出器"""

    def __init__(self):
        super().__init__("TXT")

    def get_file_extension(self) -> str:
        return ".txt"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """导出为 TXT 格式"""
        try:
            lines = []
            chat_name = kwargs.get('chat_name', '聊天记录')
            lines.append(f"= {chat_name} =")
            lines.append(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"导出工具: FriendBattle")
            lines.append("=" * 50)
            lines.append("")

            for msg in messages:
                sender = msg.get("sender", "未知")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp")

                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(timestamp, str):
                    try:
                        time_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        time_str = timestamp
                else:
                    time_str = ""

                lines.append(f"[{time_str}] {sender}: {content}")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            logger.info(f"TXT 导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"TXT 导出失败: {e}")
            return False


class MarkdownExporter(Exporter):
    """Markdown 格式导出器"""

    def __init__(self):
        super().__init__("Markdown")

    def get_file_extension(self) -> str:
        return ".md"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """导出为 Markdown 格式"""
        try:
            lines = []
            lines.append(f"# 💬 {kwargs.get('chat_name', '聊天记录')}\n")
            lines.append(f"**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"**导出工具**: FriendBattle")
            lines.append(f"**消息数量**: {len(messages)}\n")
            lines.append("---\n")

            for msg in messages:
                sender = msg.get("sender", "未知")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp")

                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M")
                elif isinstance(timestamp, str):
                    try:
                        time_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
                    except:
                        time_str = timestamp
                else:
                    time_str = ""

                lines.append(f"### {sender}")
                lines.append(f"**{time_str}**")
                lines.append(f"\n{content}\n")
                lines.append("---")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            logger.info(f"Markdown 导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Markdown 导出失败: {e}")
            return False


class CSVExporter(Exporter):
    """CSV 格式导出器"""

    def __init__(self):
        super().__init__("CSV")

    def get_file_extension(self) -> str:
        return ".csv"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """导出为 CSV 格式"""
        try:
            with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "sender", "content"])
                writer.writeheader()

                for msg in messages:
                    timestamp = msg.get("timestamp")
                    if isinstance(timestamp, datetime):
                        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(timestamp, str):
                        try:
                            timestamp = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            pass

                    writer.writerow({
                        "timestamp": timestamp,
                        "sender": msg.get("sender", "未知"),
                        "content": msg.get("content", "")
                    })

            logger.info(f"CSV 导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"CSV 导出失败: {e}")
            return False


class ExcelExporter(Exporter):
    """Excel 格式导出器"""

    def __init__(self):
        super().__init__("Excel")

    def get_file_extension(self) -> str:
        return ".xlsx"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """导出为 Excel 格式"""
        try:
            try:
                import openpyxl
            except ImportError:
                logger.warning("openpyxl 未安装，无法导出 Excel 格式")
                logger.info("提示: 运行 pip install openpyxl 来安装")
                return False

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = kwargs.get("chat_name", "聊天记录")[:31]

            # 表头
            ws.append(["时间", "发送者", "内容"])

            # 数据行
            for msg in messages:
                timestamp = msg.get("timestamp")
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass

                ws.append([
                    timestamp or "",
                    msg.get("sender", "未知"),
                    msg.get("content", "")
                ])

            # 自动调整列宽
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width

            wb.save(output_path)

            logger.info(f"Excel 导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Excel 导出失败: {e}")
            return False


class WeCloneExporter(Exporter):
    """WeClone 兼容格式导出器"""

    def __init__(self):
        super().__init__("WeClone")

    def get_file_extension(self) -> str:
        return ".txt"

    def export(self, messages: List[Dict], output_path: Path, **kwargs) -> bool:
        """
        导出为 WeClone 兼容格式

        WeClone 格式：每条消息格式为 "时间 发送者: 内容"
        """
        try:
            lines = []

            for msg in messages:
                sender = msg.get("sender", "未知")
                content = msg.get("content", "")
                timestamp = msg.get("timestamp")

                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(timestamp, str):
                    try:
                        time_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        time_str = timestamp
                else:
                    time_str = ""

                lines.append(f"{time_str}\n{sender}: {content}")

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n\n".join(lines))

            logger.info(f"WeClone 格式导出成功: {output_path}")
            return True

        except Exception as e:
            logger.error(f"WeClone 格式导出失败: {e}")
            return False


# 导出器注册表
EXPORTER_REGISTRY = {
    "chatlab": ChatLabExporter(),
    "html": HTMLExporter(),
    "json": JSONExporter(),
    "txt": TXTExporter(),
    "markdown": MarkdownExporter(),
    "csv": CSVExporter(),
    "excel": ExcelExporter(),
    "weclone": WeCloneExporter(),
}


def get_exporter(format_name: str) -> Optional[Exporter]:
    """获取指定格式的导出器"""
    return EXPORTER_REGISTRY.get(format_name.lower())


def list_export_formats() -> Dict[str, str]:
    """列出所有支持的导出格式"""
    return {
        name: exporter.name
        for name, exporter in EXPORTER_REGISTRY.items()
    }


def export_chat(
    messages: List[Dict],
    output_dir: Path,
    format_name: str,
    chat_name: str = "chat",
    **kwargs
) -> Optional[Path]:
    """
    导出聊天记录的便捷函数

    Args:
        messages: 消息列表
        output_dir: 输出目录
        format_name: 导出格式 (chatlab/html/json/txt/markdown/csv/excel/weclone)
        chat_name: 聊天名称（用于文件名）

    Returns:
        导出文件的路径，失败返回 None
    """
    exporter = get_exporter(format_name)
    if not exporter:
        logger.error(f"不支持的导出格式: {format_name}")
        return None

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_chat_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_')).strip()
    if not safe_chat_name:
        safe_chat_name = "chat"

    filename = f"{safe_chat_name}_{timestamp}{exporter.get_file_extension()}"
    output_path = output_dir / filename

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 导出
    kwargs["chat_name"] = chat_name
    success = exporter.export(messages, output_path, **kwargs)

    return output_path if success else None
