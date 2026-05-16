"""
FriendManager - 好友管理器

管理所有克隆的好友，支持导入、创建、删除、列表等操作
"""

import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from .cloner import FriendCloner, FriendProfile
from .parser import get_parser, ChatMessage


@dataclass
class FriendInfo:
    """好友信息"""
    name: str
    platform: str
    created_at: datetime
    profile_path: Optional[Path]
    memory_path: Optional[Path]
    message_count: int
    last_used_at: Optional[datetime]


class FriendManager:
    """
    好友管理器
    
    功能：
    - 导入聊天记录创建好友
    - 删除好友（连带记忆库）
    - 列出所有好友
    - 获取好友画像
    - 选择好友进行对话
    """
    
    def __init__(self, data_dir: Path = Path("data")):
        """
        初始化好友管理器
        
        Args:
            data_dir: 数据存储目录
        """
        self.data_dir = data_dir
        self.profiles_dir = data_dir / "profiles"
        self.memory_dir = data_dir / "memory"
        self.config_path = data_dir / "friends.json"
        
        # 确保目录存在
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载好友列表
        self._load_friends()
    
    def _load_friends(self):
        """加载好友列表"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.friends = {
                    name: FriendInfo(
                        name=name,
                        platform=info["platform"],
                        created_at=datetime.fromisoformat(info["created_at"]),
                        profile_path=Path(info["profile_path"]) if info.get("profile_path") else None,
                        memory_path=Path(info["memory_path"]) if info.get("memory_path") else None,
                        message_count=info.get("message_count", 0),
                        last_used_at=datetime.fromisoformat(info["last_used_at"]) if info.get("last_used_at") else None
                    )
                    for name, info in data.items()
                }
        else:
            self.friends = {}
    
    def _save_friends(self):
        """保存好友列表"""
        data = {
            name: {
                "platform": info.platform,
                "created_at": info.created_at.isoformat(),
                "profile_path": str(info.profile_path) if info.profile_path else None,
                "memory_path": str(info.memory_path) if info.memory_path else None,
                "message_count": info.message_count,
                "last_used_at": info.last_used_at.isoformat() if info.last_used_at else None
            }
            for name, info in self.friends.items()
        }
        
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def import_friend(self, chat_log_path: Path, friend_name: str, 
                     platform: str = "wechat", min_messages: int = 10) -> FriendProfile:
        """
        导入聊天记录创建好友
        
        Args:
            chat_log_path: 聊天记录文件或目录路径
            friend_name: 好友名称
            platform: 平台类型 (wechat, telegram, qq)
            min_messages: 最小消息数量要求
        
        Returns:
            FriendProfile: 创建的好友画像
        """
        # 检查好友是否已存在
        if friend_name in self.friends:
            raise ValueError(f"好友 '{friend_name}' 已存在！")
        
        # 使用MD5哈希生成安全ID
        import hashlib
        safe_id = hashlib.md5(friend_name.encode('utf-8')).hexdigest()[:16]
        
        # 创建克隆器并分析聊天记录
        cloner = FriendCloner(platform=platform)
        
        print(f"🔍 正在分析 {friend_name} 的聊天记录...")
        analysis = cloner.analyze_chat_log(chat_log_path, min_messages=min_messages)
        
        # 创建好友画像
        profile = cloner.create_profile(
            chat_log_path=chat_log_path,
            name=friend_name,
            output_dir=self.profiles_dir,
            min_messages=min_messages
        )
        
        # 创建记忆库
        memory_path = self.memory_dir / f"friend_{safe_id}"
        memory_path.mkdir(exist_ok=True)
        
        # 添加好友信息
        self.friends[friend_name] = FriendInfo(
            name=friend_name,
            platform=platform,
            created_at=datetime.now(),
            profile_path=self.profiles_dir / f"friend_{safe_id}_profile.json",
            memory_path=memory_path,
            message_count=analysis["total_messages"],
            last_used_at=None
        )
        
        self._save_friends()
        
        print(f"✅ 好友 '{friend_name}' 创建成功！")
        print(f"   - 消息数量: {analysis['total_messages']}")
        print(f"   - 语言风格: {analysis['language_style']}")
        
        return profile
    
    def delete_friend(self, friend_name: str):
        """
        删除好友（连带记忆库一起删除）
        
        Args:
            friend_name: 好友名称
        """
        if friend_name not in self.friends:
            raise ValueError(f"好友 '{friend_name}' 不存在！")
        
        friend_info = self.friends[friend_name]
        
        # 删除画像文件
        if friend_info.profile_path and friend_info.profile_path.exists():
            friend_info.profile_path.unlink()
            print(f"🗑️ 删除画像文件: {friend_info.profile_path}")
        
        # 删除记忆库目录
        if friend_info.memory_path and friend_info.memory_path.exists():
            shutil.rmtree(friend_info.memory_path)
            print(f"🗑️ 删除记忆库目录: {friend_info.memory_path}")
        
        # 从列表中移除
        del self.friends[friend_name]
        self._save_friends()
        
        print(f"✅ 好友 '{friend_name}' 已成功删除！")
    
    def get_friend_list(self) -> List[FriendInfo]:
        """
        获取所有好友列表
        
        Returns:
            好友信息列表，按创建时间排序
        """
        return sorted(self.friends.values(), key=lambda x: x.created_at)

    def list_friends(self) -> List[Dict]:
        """
        列出所有好友（字典格式）
        
        Returns:
            好友信息字典列表
        """
        return [
            {
                "name": info.name,
                "platform": info.platform,
                "created_at": info.created_at.isoformat(),
                "message_count": info.message_count,
                "last_used_at": info.last_used_at.isoformat() if info.last_used_at else None
            }
            for info in self.get_friend_list()
        ]

    def get_friend_profile(self, friend_name: str) -> FriendProfile:
        """
        获取好友画像
        
        Args:
            friend_name: 好友名称
        
        Returns:
            FriendProfile: 好友画像
        """
        if friend_name not in self.friends:
            raise ValueError(f"好友 '{friend_name}' 不存在！")
        
        friend_info = self.friends[friend_name]
        
        if not friend_info.profile_path or not friend_info.profile_path.exists():
            raise FileNotFoundError(f"未找到 '{friend_name}' 的画像文件")
        
        with open(friend_info.profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return FriendProfile(
            name=data["name"],
            language_style=data["language_style"],
            common_phrases=data["common_phrases"],
            personality_traits=data["personality_traits"],
            topics_of_interest=data["topics_of_interest"],
            vocabulary_patterns=data.get("vocabulary_patterns", {}),
            emoji_usage=data.get("emoji_usage", {}),
            avg_message_length=data.get("avg_message_length", 0.0),
            response_speed_hints=data.get("response_speed_hints", ""),
            conversation_topics=data.get("conversation_topics", []),
            typical_exchanges=data.get("typical_exchanges", []),
            humor_style=data.get("humor_style", ""),
            formality_level=data.get("formality_level", ""),
            question_frequency=data.get("question_frequency", 0.0),
            exclamation_frequency=data.get("exclamation_frequency", 0.0),
            slang_terms=data.get("slang_terms", [])
        )
    
    def select_friends_for_battle(self, friend_name1: str, friend_name2: str) -> tuple:
        """
        选择两个好友进行对话/辩论
        
        Args:
            friend_name1: 第一个好友名称
            friend_name2: 第二个好友名称
        
        Returns:
            tuple: (profile1, profile2) 两个好友的画像
        """
        if friend_name1 not in self.friends:
            raise ValueError(f"好友 '{friend_name1}' 不存在！")
        if friend_name2 not in self.friends:
            raise ValueError(f"好友 '{friend_name2}' 不存在！")
        
        # 更新最后使用时间
        self.friends[friend_name1].last_used_at = datetime.now()
        self.friends[friend_name2].last_used_at = datetime.now()
        self._save_friends()
        
        profile1 = self.get_friend_profile(friend_name1)
        profile2 = self.get_friend_profile(friend_name2)
        
        return profile1, profile2
    
    def get_friend_count(self) -> int:
        """获取好友数量"""
        return len(self.friends)
    
    def is_friend_exists(self, friend_name: str) -> bool:
        """检查好友是否存在"""
        return friend_name in self.friends
    
    def create_sample_friends(self):
        """创建示例好友（用于演示）"""
        sample_data_dir = self.data_dir / "sample_data"
        sample_data_dir.mkdir(exist_ok=True)
        
        # 创建第一个示例好友
        if "小明" not in self.friends:
            sample_file = sample_data_dir / "xiaoming.txt"
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write("""2024-01-15 10:00:00
小明: 早上好！今天天气不错啊
2024-01-15 10:01:00
用户: 是啊，适合出去玩
2024-01-15 10:02:00
小明: 我打算下午去公园散步，要不要一起？
2024-01-15 10:03:00
用户: 好啊！几点？
2024-01-15 10:04:00
小明: 下午3点吧，老地方见
2024-01-15 14:00:00
小明: 我到公园门口了，你在哪？
2024-01-15 14:01:00
用户: 马上到！
2024-01-15 14:30:00
小明: 今天的阳光真舒服
2024-01-15 14:31:00
用户: 是啊，好久没这么放松了
2024-01-15 14:32:00
小明: 周末打算干嘛？
2024-01-15 14:33:00
用户: 还没想好呢
2024-01-15 14:34:00
小明: 要不一起去看电影？新出的那部科幻片听说不错
2024-01-16 09:00:00
小明: 昨天看的电影真好看！
2024-01-16 09:01:00
用户: 是啊，特效太棒了
2024-01-16 09:02:00
小明: 下次我们再一起去看！
2024-01-16 09:03:00
用户: 好的！
2024-01-17 18:00:00
小明: 下班了吗？
2024-01-17 18:01:00
用户: 刚下班
2024-01-17 18:02:00
小明: 晚上一起吃饭？
2024-01-17 18:03:00
用户: 好啊，吃什么？
2024-01-17 18:04:00
小明: 火锅怎么样？我知道一家很好吃的
""")
            self.import_friend(sample_file, "小明", platform="wechat")
        
        # 创建第二个示例好友
        if "小红" not in self.friends:
            sample_file = sample_data_dir / "xiaohong.txt"
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write("""2024-01-15 09:00:00
小红: 早呀！今天心情好好
2024-01-15 09:01:00
用户: 怎么啦这么开心
2024-01-15 09:02:00
小红: 因为今天是周末呀！哈哈哈
2024-01-15 09:03:00
用户: 哈哈，周末打算干嘛？
2024-01-15 09:04:00
小红: 想睡个懒觉，然后逛街！
2024-01-15 12:00:00
小红: 起床啦！好饿啊
2024-01-15 12:01:00
用户: 快去吃饭
2024-01-15 12:02:00
小红: 准备点外卖，有没有推荐的？
2024-01-15 12:03:00
用户: 火锅怎么样？
2024-01-15 12:04:00
小红: 好呀好呀！我超爱火锅！🥰
2024-01-15 14:00:00
小红: 外卖到了！开吃啦
2024-01-15 14:01:00
用户: 好吃吗？
2024-01-15 14:02:00
小红: 绝绝子！太好吃了！
2024-01-16 10:00:00
小红: 今天天气真好！
2024-01-16 10:01:00
用户: 是啊
2024-01-16 10:02:00
小红: 要不要一起去公园？
2024-01-16 10:03:00
用户: 好呀
2024-01-16 15:00:00
小红: 今天玩得真开心！
2024-01-16 15:01:00
用户: 是啊
2024-01-16 15:02:00
小红: 下次再约！
2024-01-17 20:00:00
小红: 在吗在吗？
2024-01-17 20:01:00
用户: 在的
2024-01-17 20:02:00
小红: 今天看到一个超好笑的视频！
2024-01-17 20:03:00
用户: 什么视频？
2024-01-17 20:04:00
小红: 发给你！笑死我了🤣
""")
            self.import_friend(sample_file, "小红", platform="wechat")
        
        print(f"✅ 示例好友创建完成！当前好友数: {self.get_friend_count()}")