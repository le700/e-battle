"""
Debate Skills - 辩论策略模块

提供多种辩论策略，如杠精、理性派、搞笑等
优化版：更多策略，更好的提示词
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass
import random


@dataclass
class DebateContext:
    """辩论上下文"""
    topic: str
    round_num: int
    total_rounds: int
    history: list
    current_speaker: str
    opponent_speaker: str
    character_profile: Optional[Dict] = None


class BaseSkill(ABC):
    """辩论策略基类"""

    name: str = "BaseSkill"
    description: str = "基础辩论策略"
    
    # 策略的语气风格标签
    style_tags: list = []
    
    def __init__(self):
        """初始化策略，可以加入一些随机性让回复更多样化"""
        self.variation = random.randint(0, 100)

    @abstractmethod
    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """
        生成辩论回应

        Args:
            context: 辩论上下文
            opponent_view: 对手观点
            system_prompt: 系统提示词

        Returns:
            辩论回应内容
        """
        pass

    def _build_prompt(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str,
        additional_instructions: str = "",
        style_boost: str = ""
    ) -> str:
        """
        构建提示词 - 增强版
        
        增加了：
        - 更好的上下文组织
        - 角色风格强化
        - 回合策略提示
        - 回复长度控制
        """
        # 处理历史记录
        history_text = ""
        if context.history:
            history_text = "\n".join([
                f"{turn['speaker']}：{turn['content']}"
                for turn in context.history[-8:]  # 取最近8轮，避免太长
            ])
        
        # 回合策略提示
        round_strategy = ""
        if context.round_num == 1:
            round_strategy = "【第1回合】：开场要精彩，吸引注意力，鲜明表达立场！"
        elif context.round_num == context.total_rounds:
            round_strategy = "【最后1回合】：总结陈词，强化核心观点，给观众留下深刻印象！"
        else:
            round_strategy = f"【第{context.round_num}回合】：承上启下，针对对方上轮观点有力反击！"
        
        # 角色画像增强
        character_boost = ""
        if context.character_profile:
            char_info = context.character_profile
            character_boost = f"""
【角色强化信息】
语言风格：{char_info.get('language_style', '自然')}
性格特点：{', '.join(char_info.get('personality_traits', []))}
常用语参考：{', '.join(char_info.get('common_phrases', []))}
"""
        
        # 构建最终提示词
        prompt = f"""{system_prompt}

{character_boost}

{round_strategy}

辩论主题：{context.topic}
当前回合：第 {context.round_num}/{context.total_rounds} 轮

对话历史：
{history_text if history_text else '(第一轮对话)'}

对手观点：{opponent_view}

{additional_instructions}

{style_boost}

【重要要求】
1. 回复要自然口语化，不要太书面
2. 回复长度控制在50-200字之间
3. 严格以{context.current_speaker}的身份回应
4. 只需要回复内容本身，不需要前缀

现在请以 {context.current_speaker} 的身份，用符合角色特点的方式回应："""

        return prompt


class ContrarianSkill(BaseSkill):
    """杠精策略 - 总是反驳对方"""

    name = "ContrarianSkill"
    description = "杠精策略：总是反驳对方观点，善于找茬"
    style_tags = ["反驳", "挑剔", "幽默"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成杠精式回应"""
        
        # 随机化杠精的具体表现
        variations = [
            """你的辩论风格：
- 总是反驳对方，但不要人身攻击
- 善于从细节中找问题
- 语气可以带点调侃
- 偶尔可以故意曲解对方意思来反驳
- 经常用"等等"、"不对"、"你确定？"等词开头""",
            
            """你的辩论风格：
- 不管对方说什么，先反对再说
- 找对方话里的逻辑漏洞
- 用反问句质疑对方
- 举一些极端反例
- 有点小傲娇的感觉""",
            
            """你的辩论风格：
- 唱反调达人
- 鸡蛋里挑骨头
- 用调侃的方式反驳
- 让对方哭笑不得
- 偶尔承认对方"有点道理"但马上反转"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
想象你是一个爱辩论的朋友，喜欢从不同角度看问题，
喜欢反驳但不带恶意，让辩论变得有趣。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class RationalSkill(BaseSkill):
    """理性派策略 - 逻辑严密，摆事实讲道理"""

    name = "RationalSkill"
    description = "理性派策略：逻辑严密，摆事实讲道理"
    style_tags = ["逻辑", "理性", "温和"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成理性派回应"""
        
        variations = [
            """你的辩论风格：
- 逻辑严密，有理有据
- 善于举例子说明问题
- 不人身攻击，对事不对人
- 承认对方合理之处，但坚持自己的观点
- 常用"我理解你的意思，但..."这样的句式""",
            
            """你的辩论风格：
- 冷静分析，不情绪化
- 分点论述，条理清晰
- 用数据和事实说话
- 保持建设性态度
- 寻求真理而不是争输赢""",
            
            """你的辩论风格：
- 温和而坚定
- 先肯定对方，再表达不同
- 用类比和比喻让观点更易懂
- 展现思考的深度
- 让人觉得你是在真心讨论问题"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个理性思考者，用逻辑和事实来说话，
保持开放的态度，让辩论有建设性。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class HumorousSkill(BaseSkill):
    """搞笑策略 - 金句频出，幽默风趣"""

    name = "HumorousSkill"
    description = "搞笑策略：金句频出，幽默风趣"
    style_tags = ["幽默", "搞笑", "轻松"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成搞笑式回应"""
        
        variations = [
            """你的辩论风格：
- 幽默风趣，金句频出
- 善于用比喻和类比
- 自嘲和调侃对方，但不过分
- 让辩论变得有趣
- 偶尔用点网络流行语""",
            
            """你的辩论风格：
- 段子手附体
- 把严肃的辩论变成脱口秀
- 用夸张的方式表达观点
- 让大家会心一笑
- 在笑声中传递想法""",
            
            """你的辩论风格：
- 搞笑但不低俗
- 用幽默化解冲突
- 善于自黑
- 让对手也忍不住笑
- 氛围轻松愉快"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个有趣的人，能用幽默的方式表达观点，
让大家在笑声中思考，辩论变成一种享受。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class AggressiveSkill(BaseSkill):
    """激进策略 - 观点鲜明，语速快，语气强烈"""

    name = "AggressiveSkill"
    description = "激进策略：观点鲜明，语气强烈，不给对方喘息机会"
    style_tags = ["激进", "强烈", "直接"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成激进派回应"""
        
        variations = [
            """你的辩论风格：
- 观点鲜明，立场坚定
- 语气强烈有力
- 反驳直接犀利
- 常用感叹句和反问句
- 气势上压倒对方""",
            
            """你的辩论风格：
- 说话直接，不绕弯子
- 连续追问，让对方应接不暇
- 斩钉截铁，不容置疑
- 用强烈的情感表达观点
- 快节奏进攻""",
            
            """你的辩论风格：
- 简单粗暴但有效
- 直击对方弱点
- 用最直接的话表达
- 不需要铺垫
- 态度非常坚决"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个直来直去的人，有什么说什么，
态度鲜明，不拖泥带水，直接表达自己的观点。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class DiplomaticSkill(BaseSkill):
    """和事佬策略 - 试图调解双方，寻找共识"""

    name = "DiplomaticSkill"
    description = "和事佬策略：试图调解双方，寻找共识"
    style_tags = ["温和", "调解", "折中"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成和事佬式回应"""
        
        variations = [
            """你的辩论风格：
- 善于发现双方的共同点
- 试图调和矛盾
- 承认双方各有道理
- 提出折中方案或新的视角
- 促进理解和和解""",
            
            """你的辩论风格：
- 两边都不得罪
- 从更高维度看问题
- 寻求双赢方案
- 强调共同目标
- 把争论变成讨论""",
            
            """你的辩论风格：
- 温和友善
- 先肯定双方的价值
- 再提出融合的想法
- 让大家都觉得有道理
- 和平使者人设"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个和平主义者，相信沟通和理解，
善于找到双方的共同点，让辩论变成交流。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class SarcasticSkill(BaseSkill):
    """阴阳怪气策略 - 表面客气，实则讽刺"""

    name = "SarcasticSkill"
    description = "阴阳怪气策略：表面客气，实则讽刺"
    style_tags = ["讽刺", "阴阳", "高级"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成阴阳怪气式回应"""
        
        variations = [
            """你的辩论风格：
- 表面客气礼貌，实则暗藏讽刺
- 善于用"哦"、"好的"、"厉害"等词的反讽
- 不直接反驳，但让人感觉很无语
- 假装在夸对方，实际在贬低
- 高级的阴阳怪气""",
            
            """你的辩论风格：
- 明褒暗贬
- 用夸张的赞美来反衬
- 充满"善意"的建议
- 礼貌但扎心
- 让对方有苦说不出""",
            
            """你的辩论风格：
- 茶艺大师
- 无辜的语气说伤人的话
- 用"我都是为你好"的口吻
- 阴阳怪气但不失优雅
- 杀人不见血"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个"高情商"的人，用最礼貌的语气说最扎心的话，
阴阳怪气是你的拿手好戏，但不恶意伤人。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class ScholarSkill(BaseSkill):
    """老学究策略 - 引经据典，充满书生气"""

    name = "ScholarSkill"
    description = "老学究策略：引经据典，充满书生气"
    style_tags = ["学术", "引用", "稳重"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成老学究式回应"""
        
        variations = [
            """你的辩论风格：
- 引经据典，名言警句信手拈来
- 说话慢条斯理，充满智慧
- 喜欢用"古语有云..."这样的开头
- 给人一种很有学问的感觉
- 用词比较正式但不生硬""",
            
            """你的辩论风格：
- 知识渊博
- 用历史和哲学来论证
- 讲道理讲得很深
- 让人觉得很有深度
- 学者风范""",
            
            """你的辩论风格：
- 喜欢用典故
- 不疾不徐
- 每句话都有出处
- 展现学识和修养
- 以德服人"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个饱读诗书的人，用智慧和学识来辩论，
引经据典，让人信服。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class JokerSkill(BaseSkill):
    """毒舌策略 - 一针见血，说话带刺"""

    name = "JokerSkill"
    description = "毒舌策略：一针见血，说话带刺，但有道理"
    style_tags = ["毒舌", "直接", "犀利"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成毒舌式回应"""
        
        variations = [
            """你的辩论风格：
- 一针见血，直击要害
- 说话带刺但不恶毒
- 说出别人不敢说的大实话
- 虽然扎心但有道理
- 让人无法反驳""",
            
            """你的辩论风格：
- 真实得让人难受
- 不虚伪，不客套
- 撕开遮羞布
- 用最狠的话讲最真的理
- 让对方醒醒""",
            
            """你的辩论风格：
- 毒舌但善良
- 用犀利的语言点醒对方
- 不拐弯抹角
- 说实话虽难听但有用
- 嘴硬心软"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个敢说真话的人，不虚伪不客套，
用犀利的语言点破问题，虽然有点扎心但很真实。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


class LazySkill(BaseSkill):
    """摸鱼策略 - 敷衍但有趣，不想认真辩论"""

    name = "LazySkill"
    description = "摸鱼策略：敷衍但有趣，不想认真辩论"
    style_tags = ["敷衍", "摸鱼", "搞笑"]

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成摸鱼式回应"""
        
        variations = [
            """你的辩论风格：
- 不想认真辩论，想快点结束
- 回答敷衍但搞笑
- 想快点下班/休息
- 用各种理由想跑路
- 咸鱼心态""",
            
            """你的辩论风格：
- 都可以
- 随便吧
- 你说得对
- 我都行
- 别问我，问就是不知道""",
            
            """你的辩论风格：
- 摸鱼达人
- 能少说就少说
- 敷衍但可爱
- 用搞笑的方式逃避辩论
- 不想动脑子"""
        ]
        
        instructions = variations[self.variation % len(variations)]
        
        style_boost = """
【风格强化】
你是一个不想认真辩论的人，敷衍但有趣，
用搞笑的方式混过去，让人哭笑不得。
"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions,
            style_boost
        )

        return prompt


# 策略注册表 - 更新了！
SKILL_REGISTRY = {
    "contrarian": ContrarianSkill,
    "rational": RationalSkill,
    "humorous": HumorousSkill,
    "aggressive": AggressiveSkill,
    "diplomatic": DiplomaticSkill,
    "sarcastic": SarcasticSkill,
    "scholar": ScholarSkill,
    "joker": JokerSkill,
    "lazy": LazySkill,
}


def get_skill(skill_name: str) -> Optional[BaseSkill]:
    """
    根据名称获取辩论策略

    Args:
        skill_name: 策略名称

    Returns:
        对应的策略实例，如果不存在则返回None
    """
    if not skill_name:
        return None

    skill_class = SKILL_REGISTRY.get(skill_name.lower())
    if not skill_class:
        return None

    return skill_class()


def list_skills() -> Dict[str, str]:
    """
    列出所有可用的辩论策略

    Returns:
        策略名称和描述的字典
    """
    return {
        name: skill_class().description
        for name, skill_class in SKILL_REGISTRY.items()
    }


def get_random_skill() -> BaseSkill:
    """获取随机策略"""
    skill_names = list(SKILL_REGISTRY.keys())
    random_name = random.choice(skill_names)
    return get_skill(random_name)
