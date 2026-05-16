"""
微信数据库读取模块 - 独立实现版本

不依赖WeFlow，自主实现：
1. 微信路径检测
2. 密钥提取
3. 数据库读取
4. 消息解析
"""

import os
import re
import json
import struct
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
import platform

logger = logging.getLogger(__name__)


class WeChatPath:
    """微信路径管理"""

    @staticmethod
    def get_wechat_paths() -> Dict[str, Path]:
        """获取各平台微信路径"""
        system = platform.system()
        paths = {}

        if system == "Windows":
            # Windows 微信路径
            paths['exe'] = Path("C:/Program Files/Tencent/WeChat/WeChat.exe")
            paths['exe_x86'] = Path("C:/Program Files (x86)/Tencent/WeChat/WeChat.exe")
            paths['appdata'] = Path(os.getenv('APPDATA', '')) / 'Tencent' / 'WeChat'
            paths['localappdata'] = Path(os.getenv('LOCALAPPDATA', '')) / 'Tencent' / 'WeChat'
            paths['userdata'] = WeChatPath._find_userdata_windows()

        elif system == "Darwin":
            # macOS 微信路径
            paths['app'] = Path('/Applications/WeChat.app')
            paths['userdata'] = Path.home() / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'Application Support'

        elif system == "Linux":
            # Linux 微信路径
            paths['app'] = Path.home() / '.local' / 'share' / 'Tencent' / 'WeChat'
            paths['userdata'] = Path.home() / '.config' / 'Tencent' / 'WeChat'

        # 过滤不存在的路径
        return {k: v for k, v in paths.items() if v.exists() or k == 'exe' or k == 'app'}

    @staticmethod
    def _find_userdata_windows() -> Optional[Path]:
        """查找微信用户数据目录"""
        possible_paths = [
            Path(os.getenv('LOCALAPPDATA', '')) / 'Tencent' / 'WeChat',
            Path(os.getenv('APPDATA', '')) / 'Tencent' / 'WeChat',
            Path(os.getenv('USERPROFILE', '')) / 'Documents' / 'WeChat Files',
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    @staticmethod
    def find_all_versions() -> List[Dict]:
        """查找所有微信版本"""
        versions = []
        system = platform.system()

        if system == "Windows":
            search_paths = [
                Path("C:/Program Files/Tencent/WeChat"),
                Path("C:/Program Files (x86)/Tencent/WeChat"),
                Path.home() / 'AppData' / 'Local' / 'Programs' / 'WeChat',
            ]

            for base_path in search_paths:
                if base_path.exists():
                    for version_dir in base_path.iterdir():
                        if version_dir.is_dir() and version_dir.name[0].isdigit():
                            exe_path = version_dir / 'WeChat.exe'
                            if exe_path.exists():
                                versions.append({
                                    'path': version_dir,
                                    'version': version_dir.name,
                                    'exe': exe_path
                                })

        return versions


class WeChatKeyExtractor:
    """微信密钥提取器 - 简化版

    提取微信数据库的解密密钥
    支持多种提取方式
    """

    def __init__(self):
        self.key = None
        self.version = None

    def extract_key(self) -> Optional[bytes]:
        """提取数据库密钥"""
        methods = [
            self._extract_from_config,
            self._extract_from_memory,
            self._extract_from_registry,
        ]

        for method in methods:
            try:
                key = method()
                if key:
                    logger.info(f"成功提取密钥 (方法: {method.__name__})")
                    self.key = key
                    return key
            except Exception as e:
                logger.debug(f"方法 {method.__name__} 失败: {e}")

        return None

    def _extract_from_config(self) -> Optional[bytes]:
        """从配置文件提取密钥"""
        system = platform.system()

        if system == "Windows":
            return self._extract_from_config_windows()
        elif system == "Darwin":
            return self._extract_from_config_macos()
        elif system == "Linux":
            return self._extract_from_config_linux()

        return None

    def _extract_from_config_windows(self) -> Optional[bytes]:
        """从Windows配置文件提取密钥"""
        config_paths = [
            Path(os.getenv('LOCALAPPDATA', '')) / 'Tencent' / 'WeChat' / 'config' / 'Account.ini',
            Path(os.getenv('APPDATA', '')) / 'Tencent' / 'WeChat' / 'config' / 'Account.ini',
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    content = config_path.read_text(encoding='utf-8')
                    # 查找密钥信息
                    key_match = re.search(r'Key=(.+)', content)
                    if key_match:
                        return bytes.fromhex(key_match.group(1))
                except:
                    pass

        return None

    def _extract_from_config_macos(self) -> Optional[bytes]:
        """从macOS配置文件提取密钥"""
        config_paths = [
            Path.home() / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'Application Support' / 'config' / 'Account.plist',
            Path.home() / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'Preferences' / 'com.tencent.xinWeChat.plist',
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    # 使用plistlib解析
                    import plistlib
                    with open(config_path, 'rb') as f:
                        data = plistlib.load(f)
                        if 'Key' in data:
                            return data['Key']
                except:
                    pass

        return None

    def _extract_from_config_linux(self) -> Optional[bytes]:
        """从Linux配置文件提取密钥"""
        config_path = Path.home() / '.config' / 'Tencent' / 'WeChat' / 'config' / 'Account.ini'

        if config_path.exists():
            try:
                content = config_path.read_text(encoding='utf-8')
                key_match = re.search(r'Key=(.+)', content)
                if key_match:
                    return bytes.fromhex(key_match.group(1))
            except:
                pass

        return None

    def _extract_from_memory(self) -> Optional[bytes]:
        """从内存提取密钥（需要管理员权限）"""
        # 这是一个框架实现，实际需要使用ptrace或其他系统调用
        # 简化版本返回None
        logger.warning("内存提取需要系统级权限，暂未实现")
        return None

    def _extract_from_registry(self) -> Optional[bytes]:
        """从注册表提取密钥（Windows）"""
        if platform.system() != "Windows":
            return None

        try:
            import winreg
            key_path = r"SOFTWARE\Tencent\WeChat"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
            value, _ = winreg.QueryValueEx(key, "Key")
            winreg.CloseKey(key)
            return bytes.fromhex(value) if isinstance(value, str) else value
        except:
            return None


class WeChatDBReader:
    """微信数据库读取器"""

    def __init__(self, db_path: Path, key: Optional[bytes] = None):
        self.db_path = Path(db_path)
        self.key = key
        self.conn = None

    def connect(self) -> bool:
        """连接数据库"""
        try:
            if not self.db_path.exists():
                logger.error(f"数据库文件不存在: {self.db_path}")
                return False

            # 尝试使用密钥连接WCDB
            if self.key:
                # WCDB加密连接（需要WCDB库支持）
                # 这里使用SQLite作为降级方案
                try:
                    self.conn = sqlite3.connect(str(self.db_path))
                    return True
                except sqlite3.DatabaseError:
                    logger.error("数据库已加密，需要密钥")
                    return False
            else:
                # 尝试直接连接
                try:
                    self.conn = sqlite3.connect(str(self.db_path))
                    return True
                except sqlite3.DatabaseError:
                    logger.error("数据库已加密，需要密钥")
                    return False

        except Exception as e:
            logger.error(f"连接数据库失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def get_sessions(self, limit: int = 100) -> List[Dict]:
        """获取会话列表"""
        if not self.conn:
            return []

        try:
            cursor = self.conn.cursor()

            # 查询会话列表（根据微信版本不同，表名可能不同）
            queries = [
                """
                SELECT DISTINCT
                    msg.Talker,
                    MAX(msg.CreateTime) as LastTime,
                    msg.StrContent as LastMessage
                FROM
                    message msg
                WHERE msg.Type = 1
                GROUP BY msg.Talker
                ORDER BY LastTime DESC
                LIMIT ?
                """,
                """
                SELECT DISTINCT
                    msg.talker,
                    MAX(msg.createTime) as lastTime,
                    msg.strContent as lastMessage
                FROM
                    message msg
                WHERE msg.type = 1
                GROUP BY msg.talker
                ORDER BY lastTime DESC
                LIMIT ?
                """
            ]

            for query in queries:
                try:
                    cursor.execute(query, (limit,))
                    rows = cursor.fetchall()

                    sessions = []
                    for row in rows:
                        sessions.append({
                            'talker': row[0],
                            'lastTime': row[1],
                            'lastMessage': row[2] or ''
                        })

                    return sessions

                except sqlite3.OperationalError:
                    continue

            return []

        except Exception as e:
            logger.error(f"获取会话列表失败: {e}")
            return []

    def get_messages(self, talker: str, limit: int = 1000) -> List[Dict]:
        """获取消息列表"""
        if not self.conn:
            return []

        try:
            cursor = self.conn.cursor()

            queries = [
                """
                SELECT
                    msg.LocalId,
                    msg.Talker,
                    msg.Type,
                    msg.StrContent,
                    msg.CreateTime,
                    msg.IsSelf,
                    msg.SvrCreateTime
                FROM
                    message msg
                WHERE msg.Talker = ? AND msg.Type = 1
                ORDER BY msg.CreateTime DESC
                LIMIT ?
                """,
                """
                SELECT
                    msg.localId,
                    msg.talker,
                    msg.type,
                    msg.strContent,
                    msg.createTime,
                    msg.isSelf,
                    msg.svrCreateTime
                FROM
                    message msg
                WHERE msg.talker = ? AND msg.type = 1
                ORDER BY msg.createTime DESC
                LIMIT ?
                """
            ]

            for query in queries:
                try:
                    cursor.execute(query, (talker, limit))
                    rows = cursor.fetchall()

                    messages = []
                    for row in rows:
                        try:
                            timestamp = datetime.fromtimestamp(row[4] / 1000)
                        except:
                            timestamp = datetime.now()

                        messages.append({
                            'localId': row[0],
                            'talker': row[1],
                            'type': row[2],
                            'content': row[3] or '',
                            'createTime': row[4],
                            'timestamp': timestamp.isoformat(),
                            'isSelf': bool(row[5]),
                            'sender': '我' if row[5] else row[1]
                        })

                    messages.reverse()
                    return messages

                except sqlite3.OperationalError:
                    continue

            return []

        except Exception as e:
            logger.error(f"获取消息列表失败: {e}")
            return []


class WeChatScanner:
    """微信数据扫描器 - 独立实现"""

    def __init__(self):
        self.paths = WeChatPath.get_wechat_paths()
        self.key_extractor = WeChatKeyExtractor()
        self.db_readers = {}

    def scan(self) -> Dict:
        """扫描微信安装和数据"""
        result = {
            'installed': False,
            'running': False,
            'version': None,
            'userdata_path': None,
            'dbs': [],
            'key_found': False,
        }

        # 检查是否安装
        if self.paths.get('exe') and self.paths['exe'].exists():
            result['installed'] = True
            result['version'] = self._get_version()
        elif self.paths.get('app') and self.paths['app'].exists():
            result['installed'] = True

        # 查找用户数据目录
        userdata_path = self._find_userdata_path()
        if userdata_path:
            result['userdata_path'] = str(userdata_path)
            result['dbs'] = self._find_databases(userdata_path)

        # 提取密钥
        key = self.key_extractor.extract_key()
        result['key_found'] = key is not None

        # 检查是否运行
        result['running'] = self._is_wechat_running()

        return result

    def _get_version(self) -> Optional[str]:
        """获取微信版本"""
        exe_path = self.paths.get('exe')
        if exe_path and exe_path.exists():
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Tencent\WeChat")
                version, _ = winreg.QueryValueEx(key, "Version")
                winreg.CloseKey(key)
                return version
            except:
                return None
        return None

    def _find_userdata_path(self) -> Optional[Path]:
        """查找用户数据目录"""
        system = platform.system()

        if system == "Windows":
            # 常见路径
            paths = [
                Path(os.getenv('LOCALAPPDATA', '')) / 'Tencent' / 'WeChat' / 'XWeb' / 'Data',
                Path(os.getenv('LOCALAPPDATA', '')) / 'Tencent' / 'WeChat' / 'Data',
                Path(os.getenv('APPDATA', '')) / 'Tencent' / 'WeChat' / 'XWeb' / 'Data',
                Path.home() / 'Documents' / 'WeChat Files',
            ]
        elif system == "Darwin":
            paths = [
                Path.home() / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'Application Support',
                Path.home() / 'Library' / 'Containers' / 'com.tencent.xinWeChat' / 'Data' / 'Library' / 'C' / 'XWeb' / 'Data',
            ]
        else:
            paths = [
                Path.home() / '.config' / 'Tencent' / 'WeChat' / 'XWeb' / 'Data',
            ]

        for path in paths:
            if path.exists():
                return path

        return None

    def _find_databases(self, userdata_path: Path) -> List[Dict]:
        """查找数据库文件"""
        dbs = []

        # 常见数据库名称
        db_names = [
            'MSG*.db',  # 消息数据库
            'Media*.db',  # 媒体数据库
            'AppBrand*.db',  # 小程序数据库
            'Patriarch*.db',  # 收藏数据库
        ]

        for pattern in db_names:
            for db_path in userdata_path.glob(f'**/{pattern}'):
                if db_path.is_file() and db_path.stat().st_size > 0:
                    dbs.append({
                        'name': db_path.name,
                        'path': str(db_path),
                        'size': db_path.stat().st_size,
                        'modified': datetime.fromtimestamp(db_path.stat().st_mtime).isoformat()
                    })

        return dbs

    def _is_wechat_running(self) -> bool:
        """检查微信是否运行"""
        system = platform.system()

        try:
            if system == "Windows":
                import subprocess
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
                return 'WeChat.exe' in result.stdout
            elif system == "Darwin":
                import subprocess
                result = subprocess.run(['pgrep', '-a', 'WeChat'], capture_output=True, text=True)
                return result.returncode == 0
            else:
                import subprocess
                result = subprocess.run(['pgrep', '-a', 'wechat'], capture_output=True, text=True)
                return result.returncode == 0
        except:
            return False

    def read_messages(self, talker: str, limit: int = 1000) -> List[Dict]:
        """读取指定联系人的消息"""
        # 查找消息数据库
        userdata_path = self._find_userdata_path()
        if not userdata_path:
            logger.error("未找到用户数据目录")
            return []

        # 查找MSG数据库
        msg_dbs = list(userdata_path.glob('**/MSG*.db'))
        if not msg_dbs:
            logger.error("未找到消息数据库")
            return []

        # 尝试读取数据库
        for db_path in msg_dbs:
            reader = WeChatDBReader(db_path, self.key_extractor.key)
            if reader.connect():
                messages = reader.get_messages(talker, limit)
                reader.close()
                if messages:
                    return messages
                reader.close()

        return []

    def get_all_sessions(self, limit: int = 100) -> List[Dict]:
        """获取所有会话"""
        userdata_path = self._find_userdata_path()
        if not userdata_path:
            return []

        msg_dbs = list(userdata_path.glob('**/MSG*.db'))
        if not msg_dbs:
            return []

        for db_path in msg_dbs:
            reader = WeChatDBReader(db_path, self.key_extractor.key)
            if reader.connect():
                sessions = reader.get_sessions(limit)
                reader.close()
                if sessions:
                    return sessions
                reader.close()

        return []


def scan_wechat() -> Dict:
    """便捷函数：扫描微信"""
    scanner = WeChatScanner()
    return scanner.scan()


def get_wechat_sessions(limit: int = 100) -> List[Dict]:
    """便捷函数：获取所有会话"""
    scanner = WeChatScanner()
    return scanner.get_all_sessions(limit)


def get_wechat_messages(talker: str, limit: int = 1000) -> List[Dict]:
    """便捷函数：获取消息"""
    scanner = WeChatScanner()
    return scanner.read_messages(talker, limit)
