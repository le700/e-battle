"""
FriendDebate - AI好友辩论系统

让两个AI克隆的好友角色进行有趣辩论的开源项目
支持微信、Telegram、QQ 等多个平台的聊天记录导入
"""

__version__ = "0.2.0"
__author__ = "FriendDebate Team"

from .clone import FriendCloner, ChatParser, get_parser, AvatarStorage
from .debate import DebateEngine
from .share import ShareGenerator

__all__ = [
    "FriendCloner",
    "ChatParser",
    "get_parser",
    "AvatarStorage",
    "DebateEngine",
    "ShareGenerator",
]
