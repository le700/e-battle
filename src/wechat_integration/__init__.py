"""
微信数据集成模块 - 独立实现版本

完全独立，不依赖任何外部程序
集成微信数据库读取、图片解密等功能
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
import logging

from .scanner import (
    WeChatScanner,
    WeChatPath,
    WeChatKeyExtractor,
    scan_wechat,
    get_wechat_sessions,
    get_wechat_messages
)

from .image import (
    WeChatImageDecryptor,
    WeChatImageLocator,
    decrypt_wechat_images,
    find_and_decrypt_all_images
)

from .parser import (
    WeChatFileParser,
    read_wechat_export
)

logger = logging.getLogger(__name__)


class WeChatIntegration:
    """微信数据集成器

    提供统一的接口访问微信数据
    """

    def __init__(self):
        self.scanner = WeChatScanner()
        self.image_decryptor = WeChatImageDecryptor()

    def scan(self) -> Dict[str, Any]:
        """扫描微信安装和数据"""
        return self.scanner.scan()

    def get_status(self) -> Dict[str, Any]:
        """获取微信状态"""
        scan_result = self.scanner.scan()

        return {
            'installed': scan_result.get('installed', False),
            'running': scan_result.get('running', False),
            'version': scan_result.get('version'),
            'userdata_path': scan_result.get('userdata_path'),
            'database_count': len(scan_result.get('dbs', [])),
            'key_found': scan_result.get('key_found', False),
            'message': self._get_status_message(scan_result)
        }

    def _get_status_message(self, scan_result: Dict) -> str:
        """生成状态消息"""
        if not scan_result.get('installed'):
            return "未检测到微信安装"
        if not scan_result.get('userdata_path'):
            return "微信已安装但无法找到数据目录"
        if not scan_result.get('dbs'):
            return "未找到数据库文件"
        if scan_result.get('key_found'):
            return "就绪 - 已获取数据库密钥"
        else:
            return "就绪 - 请确保微信已登录并运行过"

    def get_sessions(self, limit: int = 100) -> List[Dict]:
        """获取会话列表"""
        return self.scanner.get_all_sessions(limit)

    def get_messages(self, talker: str, limit: int = 1000) -> List[Dict]:
        """获取消息"""
        return self.scanner.read_messages(talker, limit)

    def decrypt_images(self, input_dir: str, output_dir: Optional[str] = None) -> Dict:
        """解密图片"""
        return decrypt_wechat_images(input_dir, output_dir)

    def decrypt_all_images(self) -> Dict:
        """解密所有微信图片"""
        return find_and_decrypt_all_images()

    def import_friend(self, talker: str, name: Optional[str] = None, limit: int = 500) -> Optional[Dict]:
        """导入好友聊天记录

        Args:
            talker: 会话ID
            name: 好友名称（可选）
            limit: 消息数量

        Returns:
            导入的好友信息
        """
        try:
            # 获取消息
            messages = self.get_messages(talker, limit)

            if not messages:
                logger.warning(f"未找到聊天记录: {talker}")
                return None

            # 生成好友名称
            if not name:
                name = talker

            # 转换为标准格式
            standard_messages = []
            for msg in messages:
                standard_messages.append({
                    'sender': msg.get('sender', 'Unknown'),
                    'content': msg.get('content', ''),
                    'timestamp': msg.get('timestamp', '')
                })

            return {
                'name': name,
                'talker': talker,
                'message_count': len(standard_messages),
                'messages': standard_messages
            }

        except Exception as e:
            logger.error(f"导入好友失败: {e}")
            return None

    def get_friend_list(self) -> List[Dict]:
        """获取好友列表"""
        sessions = self.get_sessions(limit=200)

        friends = []
        for session in sessions:
            talker = session.get('talker', '')

            # 过滤掉群聊和非好友
            if talker.startswith('@@') or talker.startswith('gh_'):
                continue  # 跳过群聊

            friends.append({
                'id': talker,
                'name': self._get_display_name(session),
                'last_message': session.get('lastMessage', ''),
                'last_time': session.get('lastTime', 0)
            })

        return friends

    def _get_display_name(self, session: Dict) -> str:
        """获取显示名称"""
        # 尝试从会话信息中获取名称
        talker = session.get('talker', '')
        last_msg = session.get('lastMessage', '')

        # 如果有消息，尝试从消息中推断名称
        if last_msg and ':' in last_msg:
            return last_msg.split(':')[0]

        # 否则使用talker作为名称
        return talker

    def export_messages(self, talker: str, format: str = 'json', output_path: Optional[str] = None) -> Optional[str]:
        """导出消息

        Args:
            talker: 会话ID
            format: 导出格式 (json/txt/html)
            output_path: 输出路径

        Returns:
            导出文件的路径
        """
        messages = self.get_messages(talker)
        if not messages:
            return None

        if not output_path:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"wechat_export_{talker}_{timestamp}.{format}"

        output_path = Path(output_path)

        if format == 'json':
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'talker': talker,
                    'message_count': len(messages),
                    'messages': messages
                }, f, ensure_ascii=False, indent=2)

        elif format == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                for msg in messages:
                    f.write(f"[{msg.get('timestamp', '')}] {msg.get('sender', '')}: {msg.get('content', '')}\n")

        elif format == 'html':
            html_content = self._generate_html_report(talker, messages)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

        return str(output_path)

    def _generate_html_report(self, talker: str, messages: List[Dict]) -> str:
        """生成HTML报告"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>微信聊天记录 - {talker}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .message {{ margin: 10px 0; padding: 10px; border-radius: 8px; }}
        .self {{ background: #dcf8c6; margin-left: 20%; }}
        .other {{ background: #fff; margin-right: 20%; }}
        .sender {{ font-weight: bold; color: #333; }}
        .content {{ margin-top: 5px; }}
        .time {{ font-size: 0.8em; color: #888; }}
    </style>
</head>
<body>
    <h1>微信聊天记录</h1>
    <p>联系人: {talker}</p>
    <p>消息数: {len(messages)}</p>
"""

        for msg in messages:
            is_self = msg.get('isSelf', False)
            msg_class = 'self' if is_self else 'other'

            html += f"""
    <div class="message {msg_class}">
        <div class="sender">{msg.get('sender', 'Unknown')}</div>
        <div class="content">{msg.get('content', '')}</div>
        <div class="time">{msg.get('timestamp', '')}</div>
    </div>
"""

        html += """
</body>
</html>"""

        return html


# 全局实例
wechat_integration = WeChatIntegration()


def get_wechat_status() -> Dict[str, Any]:
    """便捷函数：获取微信状态"""
    return wechat_integration.get_status()


def get_wechat_friends() -> List[Dict]:
    """便捷函数：获取好友列表"""
    return wechat_integration.get_friend_list()


def get_wechat_messages(talker: str, limit: int = 1000) -> List[Dict]:
    """便捷函数：获取消息"""
    return wechat_integration.get_messages(talker, limit)


def import_wechat_friend(talker: str, name: Optional[str] = None) -> Optional[Dict]:
    """便捷函数：导入好友"""
    return wechat_integration.import_friend(talker, name)


def export_wechat_messages(talker: str, format: str = 'json') -> Optional[str]:
    """便捷函数：导出消息"""
    return wechat_integration.export_messages(talker, format)
