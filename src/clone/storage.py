"""
AvatarStorage - AI角色存储管理

管理克隆角色的数据和模型
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import asdict

from .cloner import FriendProfile


class AvatarStorage:
    """AI角色存储管理器"""

    def __init__(self, base_dir: Path):
        """
        初始化存储管理器

        Args:
            base_dir: 基础存储目录
        """
        self.base_dir = Path(base_dir)
        self.avatars_dir = self.base_dir / "avatars"
        self.avatars_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.avatars_dir / "index.json"
        self._load_index()

    def _load_index(self):
        """加载索引文件"""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def _save_index(self):
        """保存索引文件"""
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)

    def save_avatar(self, profile: FriendProfile) -> Path:
        """
        保存AI角色

        Args:
            profile: 角色画像

        Returns:
            角色存储路径
        """
        # 使用MD5哈希生成安全的角色ID（避免中文/特殊字符问题）
        import hashlib
        avatar_id = hashlib.md5(profile.name.encode('utf-8')).hexdigest()[:16]
        avatar_dir = self.avatars_dir / f"friend_{avatar_id}"
        avatar_dir.mkdir(parents=True, exist_ok=True)

        profile_data = {
            "id": avatar_id,
            "name": profile.name,
            "language_style": profile.language_style,
            "common_phrases": profile.common_phrases,
            "personality_traits": profile.personality_traits,
            "topics_of_interest": profile.topics_of_interest
        }

        profile_path = avatar_dir / "profile.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)

        self.index[avatar_id] = {
            "name": profile.name,
            "path": str(avatar_dir),
            "saved": True
        }
        self._save_index()

        return avatar_dir

    def load_avatar(self, avatar_id: str) -> Optional[Dict]:
        """
        加载AI角色

        Args:
            avatar_id: 角色ID

        Returns:
            角色数据，如果不存在返回 None
        """
        if avatar_id not in self.index:
            return None

        avatar_dir = Path(self.index[avatar_id]["path"])
        profile_path = avatar_dir / "profile.json"

        if not profile_path.exists():
            return None

        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_avatars(self) -> List[Dict]:
        """
        列出所有AI角色

        Returns:
            角色列表
        """
        return [
            {"id": avatar_id, **info}
            for avatar_id, info in self.index.items()
        ]

    def delete_avatar(self, avatar_id: str) -> bool:
        """
        删除AI角色

        Args:
            avatar_id: 角色ID

        Returns:
            是否删除成功
        """
        if avatar_id not in self.index:
            return False

        avatar_dir = Path(self.index[avatar_id]["path"])
        if avatar_dir.exists():
            shutil.rmtree(avatar_dir)

        del self.index[avatar_id]
        self._save_index()

        return True

    def avatar_exists(self, avatar_id: str) -> bool:
        """
        检查角色是否存在

        Args:
            avatar_id: 角色ID

        Returns:
            是否存在
        """
        return avatar_id in self.index

    def get_avatar_path(self, avatar_id: str) -> Optional[Path]:
        """
        获取角色目录路径

        Args:
            avatar_id: 角色ID

        Returns:
            角色目录路径
        """
        if avatar_id not in self.index:
            return None

        return Path(self.index[avatar_id]["path"])
