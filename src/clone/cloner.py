"""
FriendCloner - 好友克隆器

使用 WeClone 技术克隆好友的语言风格
支持 Telegram、微信、QQ 等多个平台
集成RAG记忆库系统实现长期记忆
"""

import json
import re
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

from .parser import ChatParser, get_parser, ChatMessage
from .memory import RAGMemoryManager


@dataclass
class FriendProfile:
    """好友画像"""
    name: str
    language_style: str
    common_phrases: List[str]
    personality_traits: List[str]
    topics_of_interest: List[str]
    # 新增特征
    vocabulary_patterns: Dict[str, int]
    emoji_usage: Dict[str, int]
    avg_message_length: float
    response_speed_hints: str
    conversation_topics: List[str]
    typical_exchanges: List[Dict[str, str]]
    humor_style: str
    formality_level: str
    question_frequency: float
    exclamation_frequency: float
    slang_terms: List[str]


class FriendCloner:
    """
    好友克隆器

    从聊天记录中分析好友的语言风格，生成角色画像
    集成RAG记忆库系统实现长期记忆
    """

    def __init__(self, platform: str = "telegram", friend_name: Optional[str] = None):
        """
        初始化克隆器

        Args:
            platform: 聊天平台 (telegram, wechat, weixin, qq)
            friend_name: 好友名称，用于初始化记忆库
        """
        self.platform = platform
        self.parser = get_parser(platform)
        self.friend_name = friend_name
        self.memory_manager = None
        if friend_name:
            self.memory_manager = RAGMemoryManager(friend_name)

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
        vocabulary_patterns = self._extract_vocabulary(messages)
        emoji_usage = self._analyze_emoji_usage(messages)
        avg_length = self._calculate_avg_length(messages)
        conversation_topics = self._extract_topics(messages)
        typical_exchanges = self._extract_typical_exchanges(messages)
        humor_style = self._analyze_humor_style(messages)
        formality_level = self._analyze_formality(messages)
        question_freq = self._calculate_question_frequency(messages)
        exclamation_freq = self._calculate_exclamation_frequency(messages)
        slang_terms = self._extract_slang(messages)
        response_speed = self._analyze_response_speed(messages)

        return {
            "total_messages": len(messages),
            "language_style": language_style,
            "common_phrases": common_phrases,
            "personality_traits": personality,
            "vocabulary_patterns": vocabulary_patterns,
            "emoji_usage": emoji_usage,
            "avg_message_length": avg_length,
            "response_speed_hints": response_speed,
            "conversation_topics": conversation_topics,
            "typical_exchanges": typical_exchanges,
            "humor_style": humor_style,
            "formality_level": formality_level,
            "question_frequency": question_freq,
            "exclamation_frequency": exclamation_freq,
            "slang_terms": slang_terms,
            "sample_messages": [msg.content for msg in messages[:50]]
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
        output_dir: Optional[Path] = None,
        min_messages: int = 100
    ) -> FriendProfile:
        """
        创建好友画像

        Args:
            chat_log_path: 聊天记录路径
            name: 好友名称
            output_dir: 输出目录
            min_messages: 最小消息数量要求

        Returns:
            好友画像
        """
        analysis = self.analyze_chat_log(chat_log_path, min_messages=min_messages)

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

    def _extract_vocabulary(self, messages: List[ChatMessage]) -> Dict[str, int]:
        """提取词汇模式"""
        words = []
        for msg in messages:
            # 简单分词（中文按字符，英文按空格）
            content = msg.content
            if any('\u4e00' <= c <= '\u9fff' for c in content):
                # 中文：提取常见词或字符组合
                words.extend(list(content))
            else:
                words.extend(content.split())
        
        counter = Counter(words)
        return dict(counter.most_common(50))
    
    def _analyze_emoji_usage(self, messages: List[ChatMessage]) -> Dict[str, int]:
        """分析表情使用"""
        emoji_pattern = re.compile('[\U00010000-\U0010ffff]', flags=re.UNICODE)
        emojis = []
        for msg in messages:
            found = emoji_pattern.findall(msg.content)
            emojis.extend(found)
        
        counter = Counter(emojis)
        return dict(counter.most_common(20))
    
    def _calculate_avg_length(self, messages: List[ChatMessage]) -> float:
        """计算平均消息长度"""
        if not messages:
            return 0.0
        total = sum(len(msg.content) for msg in messages)
        return total / len(messages)
    
    def _extract_topics(self, messages: List[ChatMessage]) -> List[str]:
        """提取话题关键词"""
        # 简单关键词提取
        keywords = []
        topic_indicators = ['今天', '明天', '昨天', '上班', '下班', '吃饭', '睡觉', 
                           '游戏', '电影', '看', '玩', '买', '去', '来', '想', '爱', '喜欢',
                           '学习', '工作', '钱', '生活', '朋友', '家人', '哈哈', '笑死', '好的',
                           '嗯', '哦', '啊', '哇', '天呐', '不会吧', '真的假的', '是吗', '对呀']
        
        content = ' '.join([msg.content for msg in messages])
        for indicator in topic_indicators:
            if indicator in content:
                keywords.append(indicator)
        
        # 去重并返回
        return list(set(keywords))[:20]
    
    def _extract_typical_exchanges(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """提取典型对话交换"""
        exchanges = []
        # 找连续的问答对
        for i in range(len(messages) - 2):
            if messages[i].sender != messages[i+1].sender:
                # 找到一个问答对
                exchanges.append({
                    'user': messages[i].content,
                    'assistant': messages[i+1].content
                })
                if len(exchanges) >= 15:  # 最多15个示例
                    break
        return exchanges
    
    def _analyze_humor_style(self, messages: List[ChatMessage]) -> str:
        """分析幽默风格"""
        humor_indicators = {
            '哈哈': 0, '笑死': 0, 'hhh': 0, '233': 0, '搞笑': 0,
            '滑稽': 0, '逗': 0, '笑哭': 0, '🤣': 0, '😂': 0
        }
        
        content = ' '.join([msg.content for msg in messages])
        for indicator in humor_indicators:
            humor_indicators[indicator] = content.count(indicator)
        
        total = sum(humor_indicators.values())
        if total > len(messages) * 0.3:
            return "非常幽默，喜欢用'哈哈'、表情符号等表达开心"
        elif total > len(messages) * 0.1:
            return "偶尔幽默，会在合适的时候开玩笑"
        else:
            return "比较严肃认真，不太常开玩笑"
    
    def _analyze_formality(self, messages: List[ChatMessage]) -> str:
        """分析正式程度"""
        formal_words = ['您好', '请问', '感谢', '打扰', '抱歉', '请您', '此致', '敬礼']
        informal_words = ['嘿', '嗨', '哟', '嘛', '啦', '呗', '咯', '哈哈哈']
        
        content = ' '.join([msg.content for msg in messages])
        formal_count = sum(content.count(word) for word in formal_words)
        informal_count = sum(content.count(word) for word in informal_words)
        
        if formal_count > informal_count:
            return "比较正式礼貌"
        elif informal_count > formal_count:
            return "非常随意口语化"
        else:
            return "适中，既不正式也不过于随意"
    
    def _calculate_question_frequency(self, messages: List[ChatMessage]) -> float:
        """计算问题频率"""
        if not messages:
            return 0.0
        question_count = sum(1 for msg in messages if '?' in msg.content or '？' in msg.content)
        return question_count / len(messages)
    
    def _calculate_exclamation_frequency(self, messages: List[ChatMessage]) -> float:
        """计算感叹号频率"""
        if not messages:
            return 0.0
        exclamation_count = sum(1 for msg in messages if '!' in msg.content or '！' in msg.content)
        return exclamation_count / len(messages)
    
    def _extract_slang(self, messages: List[ChatMessage]) -> List[str]:
        """提取网络用语/俚语"""
        common_slang = ['yyds', '绝绝子', '破防', 'emo', '躺平', '卷', '拿捏', 
                       '芜湖', '好家伙', '就这', '就离谱', '绝了', '无语子', '救命']
        content = ' '.join([msg.content.lower() for msg in messages])
        found_slang = [slang for slang in common_slang if slang in content]
        return found_slang
    
    def _analyze_response_speed(self, messages: List[ChatMessage]) -> str:
        """分析回复速度（从消息密度推断）"""
        # 简单启发式：如果消息很多且连续，说明回复快
        if len(messages) > 200:
            return "回复很快，经常秒回"
        elif len(messages) > 50:
            return "回复速度适中，不会太久"
        else:
            return "回复速度一般"
    
    def create_profile(
        self,
        chat_log_path: Path,
        name: str,
        output_dir: Optional[Path] = None,
        min_messages: int = 100
    ) -> FriendProfile:
        """
        创建好友画像

        Args:
            chat_log_path: 聊天记录路径
            name: 好友名称
            output_dir: 输出目录
            min_messages: 最小消息数量要求

        Returns:
            好友画像
        """
        analysis = self.analyze_chat_log(chat_log_path, min_messages=min_messages)

        profile = FriendProfile(
            name=name,
            language_style=analysis["language_style"],
            common_phrases=analysis["common_phrases"],
            personality_traits=analysis["personality_traits"],
            topics_of_interest=analysis["conversation_topics"],
            vocabulary_patterns=analysis["vocabulary_patterns"],
            emoji_usage=analysis["emoji_usage"],
            avg_message_length=analysis["avg_message_length"],
            response_speed_hints=analysis["response_speed_hints"],
            conversation_topics=analysis["conversation_topics"],
            typical_exchanges=analysis["typical_exchanges"],
            humor_style=analysis["humor_style"],
            formality_level=analysis["formality_level"],
            question_frequency=analysis["question_frequency"],
            exclamation_frequency=analysis["exclamation_frequency"],
            slang_terms=analysis["slang_terms"]
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
                    "topics_of_interest": profile.topics_of_interest,
                    "vocabulary_patterns": profile.vocabulary_patterns,
                    "emoji_usage": profile.emoji_usage,
                    "avg_message_length": profile.avg_message_length,
                    "response_speed_hints": profile.response_speed_hints,
                    "conversation_topics": profile.conversation_topics,
                    "typical_exchanges": profile.typical_exchanges,
                    "humor_style": profile.humor_style,
                    "formality_level": profile.formality_level,
                    "question_frequency": profile.question_frequency,
                    "exclamation_frequency": profile.exclamation_frequency,
                    "slang_terms": profile.slang_terms
                }, f, ensure_ascii=False, indent=2)

        return profile
    
    def generate_system_prompt(self, profile: FriendProfile) -> str:
        """
        生成详细的系统提示词

        Args:
            profile: 好友画像

        Returns:
            系统提示词
        """
        # 构建表情使用描述
        emoji_desc = ""
        if profile.emoji_usage:
            top_emojis = list(profile.emoji_usage.keys())[:5]
            emoji_desc = f"喜欢使用这些表情：{' '.join(top_emojis)}"
        
        # 构建常用词汇
        vocab_desc = ""
        if profile.vocabulary_patterns:
            top_words = list(profile.vocabulary_patterns.keys())[:10]
            vocab_desc = f"常用词汇：{'、'.join(top_words)}"
        
        # 构建俚语描述
        slang_desc = ""
        if profile.slang_terms:
            slang_desc = f"会使用这些网络用语：{'、'.join(profile.slang_terms)}"
        
        # 构建典型对话示例
        examples = ""
        if profile.typical_exchanges:
            examples = "以下是真实对话示例，请模仿这种风格：\n"
            for i, exchange in enumerate(profile.typical_exchanges[:8], 1):
                examples += f"\n示例 {i}:\n"
                examples += f"对方：{exchange['user']}\n"
                examples += f"{profile.name}：{exchange['assistant']}\n"
        
        prompt = f"""你正在扮演 {profile.name} 这个角色，与朋友进行对话。你的目标是完全模仿{profile.name}的说话风格、语气和思维方式。

## 角色身份与基本特征
- 你的名字是：{profile.name}
- 你正在和一位朋友聊天，请保持自然、真实的对话感觉
- 不要暴露自己是AI，也不要说"我是AI"之类的话

## 语言风格
- 总体风格：{profile.language_style}
- 正式程度：{profile.formality_level}
- 幽默风格：{profile.humor_style}
- 平均消息长度：约 {profile.avg_message_length:.0f} 字
- 回复速度：{profile.response_speed_hints}
{emoji_desc}
{vocab_desc}
{slang_desc}

## 性格特点
{chr(10).join(f'- {trait}' for trait in profile.personality_traits)}

## 常用表达与口头禅
{chr(10).join(f'- {phrase}' for phrase in profile.common_phrases[:15])}

## 常见话题
{chr(10).join(f'- {topic}' for topic in profile.conversation_topics[:10])}

## 沟通习惯
- 使用问题的频率：约 {profile.question_frequency:.0%} 的消息包含问题
- 使用感叹号的频率：约 {profile.exclamation_frequency:.0%} 的消息包含感叹号

## 重要规则
1. 始终保持{profile.name}的身份，不要切换角色
2. 使用与{profile.name}一致的语气、用词和表达习惯
3. 回复要自然流畅，符合真实聊天场景，不要过于正式或生硬
4. 根据上下文做出合理回应，参考真实对话示例的风格
5. 如果不知道说什么，可以用{profile.name}常用的表达方式回应
6. 不要过度解释，保持简洁自然，像真实朋友聊天一样
7. 可以适当使用表情符号，但要符合{profile.name}的使用习惯

{examples}

现在，请完全代入{profile.name}这个角色，开始对话！"""

        return prompt
    
    def generate_full_prompt(self, profile: FriendProfile, user_message: str, 
                            conversation_id: str = "default") -> str:
        """
        生成包含记忆上下文的完整提示词（RAG增强）
        
        Args:
            profile: 好友画像
            user_message: 当前用户消息
            conversation_id: 对话ID
            
        Returns:
            完整的系统提示词（包含记忆上下文）
        """
        # 获取基础角色提示词
        role_prompt = self.generate_system_prompt(profile)
        
        # 获取记忆上下文
        memory_context = ""
        if self.memory_manager:
            memory_context = self.memory_manager.build_context_for_prompt(
                user_message, 
                conversation_id,
                include_recent=8,
                include_relevant=5
            )
        
        # 如果有记忆上下文，添加到提示词中
        if memory_context:
            full_prompt = f"""{role_prompt}

## 对话上下文（记忆）
{memory_context}

---

请根据以上角色设定和对话记忆，以{profile.name}的身份回复以下消息：

用户：{user_message}

{profile.name}："""
        else:
            full_prompt = f"""{role_prompt}

---

请根据以上角色设定，以{profile.name}的身份回复以下消息：

用户：{user_message}

{profile.name}："""
        
        return full_prompt
    
    def update_memory(self, user_message: str, ai_response: str, 
                     conversation_id: str = "default"):
        """
        更新记忆库
        
        Args:
            user_message: 用户消息
            ai_response: AI响应
            conversation_id: 对话ID
        """
        if self.memory_manager:
            self.memory_manager.update_memory(user_message, ai_response, conversation_id)
