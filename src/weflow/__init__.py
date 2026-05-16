"""
WeFlow 集成模块

集成 WeFlow 的核心技术，包括：
- WeFlow HTTP API 调用
- 微信数据库读取
- 图片解密
- 密钥提取
"""

import json
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging
import subprocess
import platform

logger = logging.getLogger(__name__)


@dataclass
class WeFlowSession:
    """微信会话"""
    username: str
    displayName: str
    lastMessage: str
    lastTime: int
    unreadCount: int


@dataclass
class WeFlowMessage:
    """微信消息"""
    localId: int
    talker: str
    type: int  # 1=文本, 3=图片, 34=语音, 43=视频, 47=表情, 49=链接/文件
    content: str
    createTime: int
    isSelf: bool
    sender: str


@dataclass
class WeFlowContact:
    """微信联系人"""
    userName: str
    alias: str
    nickName: str
    remark: str


class WeFlowAPI:
    """WeFlow HTTP API 客户端

    WeFlow 提供本地 HTTP API 服务，默认端口 5031
    参考 WeFlow 的接口设计
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 5031):
        self.base_url = f"http://{host}:{port}"
        self.host = host
        self.port = port
        self._connected = False

    def is_available(self) -> bool:
        """检查 WeFlow API 是否可用"""
        try:
            import urllib.request
            url = f"{self.base_url}/health"
            with urllib.request.urlopen(url, timeout=2) as response:
                data = json.loads(response.read().decode())
                self._connected = data.get("status") == "ok"
                return self._connected
        except Exception as e:
            logger.warning(f"WeFlow API 不可用: {e}")
            self._connected = False
            return False

    def get_health(self) -> bool:
        """健康检查"""
        return self.is_available()

    def get_sessions(self, keyword: str = "", limit: int = 100) -> List[WeFlowSession]:
        """获取会话列表

        参考: GET /api/v1/sessions
        """
        try:
            import urllib.request
            import urllib.parse

            params = f"?limit={limit}"
            if keyword:
                params += f"&keyword={urllib.parse.quote(keyword)}"

            url = f"{self.base_url}/api/v1/sessions{params}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

                if not data.get("success"):
                    logger.error(f"获取会话失败: {data.get('error')}")
                    return []

                sessions = []
                for item in data.get("sessions", []):
                    sessions.append(WeFlowSession(
                        username=item.get("username", ""),
                        displayName=item.get("displayName", item.get("username", "")),
                        lastMessage=item.get("lastMessage", ""),
                        lastTime=item.get("lastTime", 0),
                        unreadCount=item.get("unreadCount", 0)
                    ))

                return sessions

        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            return []

    def get_messages(
        self,
        talker: str,
        limit: int = 100,
        offset: int = 0,
        start: str = "",
        end: str = "",
        chatlab_format: bool = False
    ) -> List[WeFlowMessage]:
        """获取消息列表

        参考: GET /api/v1/messages
        """
        try:
            import urllib.request
            import urllib.parse

            params = [
                ("talker", talker),
                ("limit", str(limit)),
                ("offset", str(offset)),
            ]

            if start:
                params.append(("start", start))
            if end:
                params.append(("end", end))
            if chatlab_format:
                params.append(("chatlab", "1"))

            url = f"{self.base_url}/api/v1/messages?{urllib.parse.urlencode(params)}"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

                if not data.get("success"):
                    logger.error(f"获取消息失败: {data.get('error')}")
                    return []

                messages = []
                for item in data.get("messages", []):
                    messages.append(WeFlowMessage(
                        localId=item.get("localId", 0),
                        talker=item.get("talker", ""),
                        type=item.get("type", 1),
                        content=item.get("content", ""),
                        createTime=item.get("createTime", 0),
                        isSelf=item.get("isSelf", False),
                        sender=item.get("sender", "")
                    ))

                return messages

        except Exception as e:
            logger.error(f"获取消息列表失败: {e}")
            return []

    def get_messages_as_chatlab(self, talker: str, limit: int = 100) -> Dict:
        """以 ChatLab 格式获取消息

        ChatLab 是标准化的聊天记录格式
        """
        try:
            import urllib.request
            import urllib.parse

            params = urllib.parse.urlencode({
                "talker": talker,
                "limit": str(limit),
                "chatlab": "1"
            })

            url = f"{self.base_url}/api/v1/messages?{params}"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

                if not data.get("success"):
                    logger.error(f"获取 ChatLab 消息失败: {data.get('error')}")
                    return {}

                return data

        except Exception as e:
            logger.error(f"获取 ChatLab 格式消息失败: {e}")
            return {}

    def get_contacts(self, keyword: str = "", limit: int = 100) -> List[WeFlowContact]:
        """获取联系人列表

        参考: GET /api/v1/contacts
        """
        try:
            import urllib.request
            import urllib.parse

            params = f"?limit={limit}"
            if keyword:
                params += f"&keyword={urllib.parse.quote(keyword)}"

            url = f"{self.base_url}/api/v1/contacts{params}"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

                if not data.get("success"):
                    logger.error(f"获取联系人失败: {data.get('error')}")
                    return []

                contacts = []
                for item in data.get("contacts", []):
                    contacts.append(WeFlowContact(
                        userName=item.get("userName", ""),
                        alias=item.get("alias", ""),
                        nickName=item.get("nickName", ""),
                        remark=item.get("remark", "")
                    ))

                return contacts

        except Exception as e:
            logger.error(f"获取联系人列表失败: {e}")
            return []

    def get_conversation_name(self, talker: str) -> str:
        """获取会话名称（联系人昵称或群名）"""
        contacts = self.get_contacts(keyword=talker, limit=10)
        for contact in contacts:
            if contact.userName == talker:
                return contact.nickName or contact.remark or contact.alias or talker
        return talker


class WeFlowIntegrator:
    """WeFlow 集成器

    将 WeFlow 的功能集成到 FriendBattle 中
    """

    def __init__(self):
        self.api = WeFlowAPI()
        self._weflow_installed = False
        self._weflow_path = None

    def check_weflow(self) -> Dict[str, Any]:
        """检查 WeFlow 是否已安装并运行"""
        result = {
            "installed": False,
            "running": False,
            "api_available": False,
            "path": None,
            "message": ""
        }

        # 检查 WeFlow 是否安装
        weflow_path = self._find_weflow()
        result["installed"] = weflow_path is not None
        result["path"] = weflow_path

        if not weflow_path:
            result["message"] = "未找到 WeFlow，请先安装 WeFlow"
            return result

        # 检查 WeFlow 是否运行
        result["running"] = self._is_weflow_running()

        if not result["running"]:
            result["message"] = "WeFlow 未运行，请启动 WeFlow"
            return result

        # 检查 API 是否可用
        result["api_available"] = self.api.is_available()

        if not result["api_available"]:
            result["message"] = "WeFlow API 不可用，请确保在设置中启用了 API 服务"
            return result

        result["message"] = "WeFlow 已就绪"
        return result

    def _find_weflow(self) -> Optional[Path]:
        """查找 WeFlow 安装路径"""
        system = platform.system()

        if system == "Windows":
            paths = [
                Path("C:/Program Files/WeFlow/WeFlow.exe"),
                Path("C:/Program Files (x86)/WeFlow/WeFlow.exe"),
                Path.home() / "AppData/Local/Programs/WeFlow/WeFlow.exe",
            ]
        elif system == "Darwin":  # macOS
            paths = [
                Path("/Applications/WeFlow.app"),
                Path.home() / "Applications/WeFlow.app",
            ]
        else:  # Linux
            paths = [
                Path("/usr/bin/weflow"),
                Path("/usr/local/bin/weflow"),
                Path.home() / ".local/bin/weflow",
            ]

        for path in paths:
            if path.exists():
                self._weflow_path = path
                return path

        return None

    def _is_weflow_running(self) -> bool:
        """检查 WeFlow 是否在运行"""
        system = platform.system()

        try:
            if system == "Windows":
                result = subprocess.run(
                    ["tasklist"], capture_output=True, text=True
                )
                return "WeFlow.exe" in result.stdout
            else:
                result = subprocess.run(
                    ["pgrep", "-a", "weflow"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0

        except Exception as e:
            logger.error(f"检查 WeFlow 运行状态失败: {e}")
            return False

    def launch_weflow(self) -> bool:
        """启动 WeFlow"""
        if not self._weflow_path:
            self._find_weflow()

        if not self._weflow_path:
            logger.error("未找到 WeFlow 可执行文件")
            return False

        try:
            subprocess.Popen(
                [str(self._weflow_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 等待 WeFlow 启动
            for _ in range(30):
                time.sleep(1)
                if self.api.is_available():
                    return True

            logger.error("WeFlow 启动超时")
            return False

        except Exception as e:
            logger.error(f"启动 WeFlow 失败: {e}")
            return False

    def get_all_conversations(self) -> List[Dict]:
        """获取所有会话列表"""
        sessions = self.api.get_sessions(limit=100)

        result = []
        for session in sessions:
            name = self.api.get_conversation_name(session.username)
            result.append({
                "id": session.username,
                "name": name,
                "displayName": session.displayName,
                "lastMessage": session.lastMessage,
                "lastTime": session.lastTime,
                "unreadCount": session.unreadCount,
            })

        return result

    def get_chat_history(
        self,
        talker: str,
        limit: int = 500,
        as_chatlab: bool = True
    ) -> List[Dict]:
        """获取聊天历史记录

        Args:
            talker: 会话ID
            limit: 消息数量限制
            as_chatlab: 是否返回 ChatLab 格式

        Returns:
            消息列表
        """
        if as_chatlab:
            data = self.api.get_messages_as_chatlab(talker, limit)
            if data:
                return data.get("messages", [])
        else:
            messages = self.api.get_messages(talker, limit)
            return [
                {
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.createTime,
                    "type": msg.type,
                    "isSelf": msg.isSelf,
                }
                for msg in messages
            ]

        return []

    def get_contact_info(self, talker: str) -> Optional[Dict]:
        """获取联系人详细信息"""
        contacts = self.api.get_contacts(keyword=talker, limit=10)

        for contact in contacts:
            if contact.userName == talker:
                return {
                    "userName": contact.userName,
                    "alias": contact.alias,
                    "nickName": contact.nickName,
                    "remark": contact.remark,
                }

        return None


# 全局实例
weflow_integrator = WeFlowIntegrator()


def check_weflow_status() -> Dict[str, Any]:
    """检查 WeFlow 状态"""
    return weflow_integrator.check_weflow()


def is_weflow_available() -> bool:
    """检查 WeFlow 是否可用"""
    status = check_weflow_status()
    return status.get("api_available", False)


def get_weflow_sessions() -> List[Dict]:
    """获取所有会话"""
    return weflow_integrator.get_all_conversations()


def get_weflow_chat_history(talker: str, limit: int = 500) -> List[Dict]:
    """获取聊天历史"""
    return weflow_integrator.get_chat_history(talker, limit)
