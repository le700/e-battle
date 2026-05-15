"""
FriendClone - 好友克隆模块

基于 WeClone 技术，从聊天记录中克隆好友的语言风格
支持平台：Telegram, WeChat, QQ 等
"""

from .parser import ChatParser, get_parser
from .cloner import FriendCloner
from .storage import AvatarStorage

__all__ = ["ChatParser", "get_parser", "FriendCloner", "AvatarStorage"]
