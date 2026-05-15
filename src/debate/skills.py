"""
Debate Skills - 辩论策略模块

提供多种辩论策略，如杠精、理性派、搞笑等
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class DebateContext:
    """辩论上下文"""
    topic: str
    round_num: int
    total_rounds: int
    history: list
    current_speaker: str
    opponent_speaker: str


class BaseSkill(ABC):
    """辩论策略基类"""

    name: str = "BaseSkill"
    description: str = "基础辩论策略"

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
        additional_instructions: str = ""
    ) -> str:
        """构建提示词"""
        history_text = "\n".join([
            f"{turn['speaker']}：{turn['content']}"
            for turn in context.history[-10:]
        ])

        prompt = f"""{system_prompt}

辩论主题：{context.topic}
当前回合：第 {context.round_num}/{context.total_rounds} 轮

对话历史：
{history_text}

对手观点：{opponent_view}

{additional_instructions}

请以 {context.current_speaker} 的身份，用符合角色特点的方式回应："""

        return prompt


class ContrarianSkill(BaseSkill):
    """杠精策略 - 总是反驳对方"""

    name = "ContrarianSkill"
    description = "杠精策略：总是反驳对方观点，善于找茬"

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成杠精式回应"""
        instructions = """你的辩论风格：
- 总是反驳对方，但不要人身攻击
- 善于从细节中找问题
- 语气可以带点调侃
- 偶尔可以故意曲解对方意思来反驳

请用符合这个风格的方式回应，注意保持幽默但有力的辩论。"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions
        )

        return prompt


class RationalSkill(BaseSkill):
    """理性派策略 - 逻辑严密，摆事实讲道理"""

    name = "RationalSkill"
    description = "理性派策略：逻辑严密，摆事实讲道理"

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成理性派回应"""
        instructions = """你的辩论风格：
- 逻辑严密，有理有据
- 善于举例子说明问题
- 不人身攻击，对事不对人
- 承认对方合理之处，但坚持自己的观点

请用符合这个风格的方式回应，展现理性和智慧。"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions
        )

        return prompt


class HumorousSkill(BaseSkill):
    """搞笑策略 - 金句频出，幽默风趣"""

    name = "HumorousSkill"
    description = "搞笑策略：金句频出，幽默风趣"

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成搞笑式回应"""
        instructions = """你的辩论风格：
- 幽默风趣，金句频出
- 善于用比喻和类比
- 自嘲和调侃对方，但不过分
- 让辩论变得有趣

请用符合这个风格的方式回应，让辩论充满欢乐。"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions
        )

        return prompt


class AggressiveSkill(BaseSkill):
    """激进策略 - 观点鲜明，语速快，语气强烈"""

    name = "AggressiveSkill"
    description = "激进策略：观点鲜明，语气强烈，不给对方喘息机会"

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成激进派回应"""
        instructions = """你的辩论风格：
- 观点鲜明，立场坚定
- 语气强烈有力
- 反驳直接犀利
- 常用感叹句和反问句

请用符合这个风格的方式回应，展现强大的气势。"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions
        )

        return prompt


class DiplomaticSkill(BaseSkill):
    """和事佬策略 - 试图调解双方，寻找共识"""

    name = "DiplomaticSkill"
    description = "和事佬策略：试图调解双方，寻找共识"

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成和事佬式回应"""
        instructions = """你的辩论风格：
- 善于发现双方的共同点
- 试图调和矛盾
- 承认双方各有道理
- 提出折中方案或新的视角

请用符合这个风格的方式回应，促进理解和和解。"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions
        )

        return prompt


class SarcasticSkill(BaseSkill):
    """阴阳怪气策略 - 表面客气，实则讽刺"""

    name = "SarcasticSkill"
    description = "阴阳怪气策略：表面客气，实则讽刺"

    def generate_response(
        self,
        context: DebateContext,
        opponent_view: str,
        system_prompt: str
    ) -> str:
        """生成阴阳怪气式回应"""
        instructions = """你的辩论风格：
- 表面客气礼貌，实则暗藏讽刺
- 善于用"哦"、"好的"、"厉害"等词的反讽
- 不直接反驳，但让人感觉很无语
- 假装在夸对方，实际在贬低

请用符合这个风格的方式回应，展现高级的讽刺技巧。"""

        prompt = self._build_prompt(
            context,
            opponent_view,
            system_prompt,
            instructions
        )

        return prompt


def get_skill(skill_name: str) -> BaseSkill:
    """
    根据名称获取辩论策略

    Args:
        skill_name: 策略名称

    Returns:
        对应的策略实例
    """
    skills = {
        "contrarian": ContrarianSkill,
        "rational": RationalSkill,
        "humorous": HumorousSkill,
        "aggressive": AggressiveSkill,
        "diplomatic": DiplomaticSkill,
        "sarcastic": SarcasticSkill,
    }

    skill_class = skills.get(skill_name.lower())
    if not skill_class:
        raise ValueError(f"未知的策略：{skill_name}")

    return skill_class()


SKILL_REGISTRY = {
    "contrarian": ContrarianSkill,
    "rational": RationalSkill,
    "humorous": HumorousSkill,
    "aggressive": AggressiveSkill,
    "diplomatic": DiplomaticSkill,
    "sarcastic": SarcasticSkill,
}


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
