"""
FriendCloner - 好友克隆器

使用 WeClone 技术克隆好友的语言风格
支持 Telegram、微信、QQ 等多个平台
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from .parser import ChatParser, get_parser, ChatMessage


@dataclass
class FriendProfile:
    """好友画像"""
    name: str
    language_style: str
    common_phrases: List[str]
    personality_traits: List[str]
    topics_of_interest: List[str]


class FriendCloner:
    """
    好友克隆器

    从聊天记录中分析好友的语言风格，生成角色画像
    """

    def __init__(self, platform: str = "telegram"):
        """
        初始化克隆器

        Args:
            platform: 聊天平台 (telegram, wechat, weixin, qq)
        """
        self.platform = platform
        self.parser = get_parser(platform)

    def analyze_chat_log(
        self,
        chat_log_path: Path,
        min_messages: int = 100
    ) -> Dict:
        """
        分析聊天记录，提取好友特征

        Args:
            chat_log_path: 聊天记录文件夹路径
            min_messages: 最少需要的消息数量

        Returns:
            分析结果字典
        """
        messages = self.parser.parse(chat_log_path)

        if len(messages) < min_messages:
            raise ValueError(
                f"聊天记录太少: {len(messages)} 条，"
                f"建议至少 {min_messages} 条以获得更好的克隆效果"
            )

        common_phrases = self._extract_common_phrases(messages)
        language_style = self._analyze_language_style(messages)
        personality = self._analyze_personality(messages)

        return {
            "total_messages": len(messages),
            "language_style": language_style,
            "common_phrases": common_phrases,
            "personality_traits": personality,
            "sample_messages": [msg.content for msg in messages[:20]]
        }

    def _extract_common_phrases(self, messages: List[ChatMessage]) -> List[str]:
        """提取常用短语"""
        phrase_counts = {}

        for msg in messages:
            content = msg.content.strip()
            if len(content) < 10:
                continue

            words = content.split()
            for i in range(len(words) - 2):
                phrase = " ".join(words[i:i+3])
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1

        sorted_phrases = sorted(
            phrase_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [phrase for phrase, count in sorted_phrases[:20]]

    def _analyze_language_style(self, messages: List[ChatMessage]) -> str:
        """分析语言风格"""
        total_chars = sum(len(msg.content) for msg in messages)
        avg_length = total_chars / len(messages) if messages else 0

        emoji_count = sum(
            1 for msg in messages
            if any(ord(c) > 127000 for c in msg.content)
        )
        emoji_ratio = emoji_count / len(messages) if messages else 0

        question_count = sum(
            1 for msg in messages
            if "？" in msg.content or "?" in msg.content
        )

        exclamation_count = sum(
            1 for msg in messages
            if "！" in msg.content or "!" in msg.content
        )

        style_desc = []

        if avg_length < 20:
            style_desc.append("简短精炼")
        elif avg_length < 50:
            style_desc.append("适中自然")
        elif avg_length < 100:
            style_desc.append("详细啰嗦")
        else:
            style_desc.append("长篇大论")

        if emoji_ratio > 0.3:
            style_desc.append("爱用表情包")
        elif emoji_ratio > 0.1:
            style_desc.append("偶尔用表情")

        if question_count / len(messages) > 0.2:
            style_desc.append("爱问问题")

        if exclamation_count / len(messages) > 0.15:
            style_desc.append("语气强烈")

        chinese_chars = sum(1 for msg in messages for c in msg.content if '\u4e00' <= c <= '\u9fff')
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0

        if chinese_ratio > 0.5:
            style_desc.append("中文为主")
        else:
            style_desc.append("中英混合")

        return "，".join(style_desc) if style_desc else "普通"

    def _analyze_personality(self, messages: List[ChatMessage]) -> List[str]:
        """分析性格特征"""
        traits = []

        positive_words = ["好", "棒", "赞", "喜欢", "开心", "哈哈", "厉害", "good", "great", "nice"]
        negative_words = ["不好", "讨厌", "无语", "生气", "烦", "not", "bad", "hate", "angry"]
        question_words = ["怎么", "为什么", "是不是", "能不能", "what", "why", "how"]
        agreement_words = ["对", "是", "没错", "agree", "yes", "right"]
        disagreement_words = ["不是", "不对", "错", "no", "wrong", "disagree"]

        positive_count = sum(
            sum(1 for w in positive_words if w in msg.content.lower())
            for msg in messages
        )
        negative_count = sum(
            sum(1 for w in negative_words if w in msg.content.lower())
            for msg in messages
        )
        question_count = sum(
            sum(1 for w in question_words if w in msg.content)
            for msg in messages
        )
        agreement_count = sum(
            sum(1 for w in agreement_words if w in msg.content)
            for msg in messages
        )
        disagreement_count = sum(
            sum(1 for w in disagreement_words if w in msg.content)
            for msg in messages
        )

        ratio = max(len(messages), 1)

        if positive_count / ratio > 0.3:
            traits.append("乐观积极")
        if negative_count / ratio > 0.2:
            traits.append("消极抱怨")
        if question_count / ratio > 0.3:
            traits.append("好奇心强")
        if agreement_count / ratio > 0.15:
            traits.append("温和友善")
        if disagreement_count / ratio > 0.1:
            traits.append("敢于质疑")

        if positive_count < ratio * 0.1 and negative_count < ratio * 0.1:
            traits.append("理性冷静")

        return traits if traits else ["普通"]

    def create_profile(
        self,
        chat_log_path: Path,
        name: str,
        output_dir: Optional[Path] = None
    ) -> FriendProfile:
        """
        创建好友画像

        Args:
            chat_log_path: 聊天记录路径
            name: 好友名称
            output_dir: 输出目录

        Returns:
            好友画像
        """
        analysis = self.analyze_chat_log(chat_log_path)

        profile = FriendProfile(
            name=name,
            language_style=analysis["language_style"],
            common_phrases=analysis["common_phrases"],
            personality_traits=analysis["personality_traits"],
            topics_of_interest=[]
        )

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            profile_path = output_dir / f"{name}_profile.json"
            with open(profile_path, "w", encoding="utf-8") as f:
                json.dump({
                    "name": profile.name,
                    "platform": self.platform,
                    "language_style": profile.language_style,
                    "common_phrases": profile.common_phrases,
                    "personality_traits": profile.personality_traits,
                    "topics_of_interest": profile.topics_of_interest
                }, f, ensure_ascii=False, indent=2)

        return profile

    def generate_system_prompt(self, profile: FriendProfile) -> str:
        """
        生成系统提示词

        Args:
            profile: 好友画像

        Returns:
            系统提示词
        """
        prompt = f"""你正在扮演 {profile.name} 这个角色。

角色特征：
- 说话风格：{profile.language_style}
- 性格特点：{", ".join(profile.personality_traits)}

常用表达：
{chr(10).join(f"- {phrase}" for phrase in profile.common_phrases[:10])}

请保持角色特征，用 {profile.name} 的语气和风格进行对话。
不要偏离角色设定。"""

        return prompt
