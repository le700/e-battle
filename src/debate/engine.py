"""
Debate Engine - 辩论核心引擎

管理辩论流程，对阵双方，策略注入等核心功能
"""

import uuid
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from .skills import BaseSkill, ContrarianSkill


class DebateStatus(Enum):
    """辩论状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class DebateTurn:
    """辩论回合"""
    round_num: int
    speaker: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    skill_used: str = ""

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "round_num": self.round_num,
            "speaker": self.speaker,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "skill_used": self.skill_used
        }


@dataclass
class Debate:
    """辩论记录"""
    id: str
    topic: str
    status: DebateStatus
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    turns: List[DebateTurn] = field(default_factory=list)
    debaters: List[str] = field(default_factory=list)
    skills: Dict[str, str] = field(default_factory=dict)

    @property
    def debater1(self) -> str:
        """辩手1"""
        return self.debaters[0] if len(self.debaters) > 0 else ""
    
    @property
    def debater2(self) -> str:
        """辩手2"""
        return self.debaters[1] if len(self.debaters) > 1 else ""
    
    @property
    def skill1(self) -> str:
        """辩手1策略"""
        return self.skills.get(self.debater1, "")
    
    @property
    def skill2(self) -> str:
        """辩手2策略"""
        return self.skills.get(self.debater2, "")
    
    @property
    def is_multiplayer(self) -> bool:
        """是否是多人模式"""
        return len(self.debaters) > 2
    
    def add_turn(self, speaker: str, content: str, skill_used: str = ""):
        """添加辩论回合"""
        speaker_turns = [t for t in self.turns if t.speaker == speaker]
        round_num = len(speaker_turns) + 1
        turn = DebateTurn(
            round_num=round_num,
            speaker=speaker,
            content=content,
            skill_used=skill_used
        )
        self.turns.append(turn)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "topic": self.topic,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "turns": [turn.to_dict() for turn in self.turns],
            "debaters": self.debaters,
            "debater1": self.debater1,
            "debater2": self.debater2,
            "skills": self.skills,
            "mode": "multiplayer" if self.is_multiplayer else "duel",
            "player_count": len(self.debaters)
        }

    def save(self, output_dir: Path):
        """保存辩论记录"""
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / f"{self.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return file_path


@dataclass
class Debater:
    """辩手"""
    name: str
    model_path: Optional[str] = None
    profile_data: Optional[Dict] = None
    skill: BaseSkill = field(default_factory=lambda: ContrarianSkill())

    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        if self.profile_data:
            name = self.profile_data.get("name", self.name)
            style = self.profile_data.get("language_style", "普通")
            traits = self.profile_data.get("personality_traits", [])
            phrases = self.profile_data.get("common_phrases", [])

            prompt = f"""你正在扮演 {name} 这个角色。

说话风格：{style}
性格特点：{", ".join(traits)}

请保持角色特征，用 {name} 的语气和风格进行辩论。
不要偏离角色设定。"""
            return prompt

        return f"你正在扮演 {self.name}，请保持角色特征进行辩论。"


class DebateEngine:
    """
    辩论引擎

    管理辩论流程，支持策略注入，多轮对话等
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化辩论引擎

        Args:
            output_dir: 辩论记录输出目录
        """
        self.output_dir = output_dir or Path("data/debates")
        self.debaters: Dict[str, Debater] = {}
        self.debates: Dict[str, Debate] = {}
        self.model_loader: Optional[Callable] = None

    def add_debater(
        self,
        name: str,
        model_path: Optional[str] = None,
        profile_data: Optional[Dict] = None,
        skill: Optional[BaseSkill] = None
    ):
        """
        添加辩手

        Args:
            name: 辩手名称
            model_path: 模型路径
            profile_data: 角色数据
            skill: 辩论策略
        """
        self.debaters[name] = Debater(
            name=name,
            model_path=model_path,
            profile_data=profile_data,
            skill=skill or ContrarianSkill()
        )

    def set_model_loader(self, loader: Callable):
        """
        设置模型加载器

        Args:
            loader: 模型加载函数，接收 name 参数，返回模型实例
        """
        self.model_loader = loader

    def _load_model(self, name: str):
        """加载模型"""
        if self.model_loader and name in self.debaters:
            debater = self.debaters[name]
            if debater.model_path:
                return self.model_loader(debater.model_path)
        return None

    def start(
        self,
        topic: str,
        rounds: int = 5,
        max_tokens: int = 300,
        temperature: float = 0.8
    ) -> Debate:
        """
        开始辩论

        Args:
            topic: 辩论主题
            rounds: 辩论回合数（每人发言次数）
            max_tokens: 最大生成token数
            temperature: 温度参数

        Returns:
            辩论记录
        """
        if len(self.debaters) < 2:
            raise ValueError("辩论至少需要两个辩手")
        
        is_multiplayer = len(self.debaters) > 2
        debater_names = list(self.debaters.keys())
        
        debate = Debate(
            id=str(uuid.uuid4())[:8],
            topic=topic,
            status=DebateStatus.IN_PROGRESS,
            debaters=debater_names,
            skills={name: self.debaters[name].skill.name for name in debater_names}
        )

        print(f"\n{'='*60}")
        print(f"辩论主题：{topic}")
        print(f"模式：{'多人Battle' if is_multiplayer else '双人Battle'}")
        print(f"参赛者：{', '.join([f'{name} ({self.debaters[name].skill.name})' for name in debater_names])}")
        print(f"{'='*60}\n")

        debate.add_turn(
            speaker="System",
            content=f"辩论主题：{topic} | 模式：{'多人Battle' if is_multiplayer else '双人Battle'}",
            skill_used="System"
        )

        if is_multiplayer:
            self._run_multiplayer_battle(
                debate, topic, debater_names, rounds, max_tokens, temperature
            )
        else:
            self._run_duel_battle(
                debate, topic, debater_names, rounds, max_tokens, temperature
            )

        debate.status = DebateStatus.COMPLETED
        debate.completed_at = datetime.now()
        debate.save(self.output_dir)

        print(f"\n{'='*60}")
        print(f"辩论结束！共 {len([t for t in debate.turns if t.speaker != 'System'])} 轮")
        print(f"辩论记录已保存至：{debate.save(self.output_dir)}")
        print(f"{'='*60}\n")

        return debate

    def _run_duel_battle(
        self,
        debate: Debate,
        topic: str,
        debater_names: List[str],
        rounds: int,
        max_tokens: int,
        temperature: float
    ):
        """双人Battle"""
        for round_num in range(1, rounds + 1):
            print(f"\n--- 第 {round_num} 轮 ---")

            for debater_name in debater_names:
                opponent_name = debater_names[1] if debater_name == debater_names[0] else debater_names[0]

                context = DebateContext(
                    topic=topic,
                    round_num=round_num,
                    total_rounds=rounds,
                    history=[turn.to_dict() for turn in debate.turns[1:]],
                    current_speaker=debater_name,
                    opponent_speaker=opponent_name
                )

                response = self._generate_response(
                    debater_name=debater_name,
                    opponent_name=opponent_name,
                    context=context,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                debate.add_turn(
                    speaker=debater_name,
                    content=response,
                    skill_used=self.debaters[debater_name].skill.name
                )

                print(f"{debater_name}: {response}\n")

    def _run_multiplayer_battle(
        self,
        debate: Debate,
        topic: str,
        debater_names: List[str],
        rounds: int,
        max_tokens: int,
        temperature: float
    ):
        """多人Battle"""
        num_players = len(debater_names)
        
        for round_num in range(1, rounds + 1):
            print(f"\n{'='*40}")
            print(f"第 {round_num} 轮 - 多人Battle")
            print(f"{'='*40}")

            for i, debater_name in enumerate(debater_names):
                opponents = [name for name in debater_names if name != debater_name]
                other_speakers = [t["speaker"] for t in debate.turns[1:] if t["speaker"] != debater_name]
                last_opponent = other_speakers[-1] if other_speakers else "无"
                
                context = DebateContext(
                    topic=topic,
                    round_num=round_num,
                    total_rounds=rounds,
                    history=[turn.to_dict() for turn in debate.turns[1:]],
                    current_speaker=debater_name,
                    opponent_speaker=", ".join(opponents)
                )

                response = self._generate_response(
                    debater_name=debater_name,
                    opponent_name=", ".join(opponents),
                    context=context,
                    max_tokens=max_tokens,
                    temperature=temperature
                )

                debate.add_turn(
                    speaker=debater_name,
                    content=response,
                    skill_used=self.debaters[debater_name].skill.name
                )

                print(f"\n💬 {debater_name} [{i+1}/{num_players}]:")
                print(f"   {response}")

    def _generate_response(
        self,
        debater_name: str,
        opponent_name: str,
        context: 'DebateContext',
        max_tokens: int,
        temperature: float
    ) -> str:
        """
        生成辩手回应

        Args:
            debater_name: 当前辩手名称
            opponent_name: 对手名称
            context: 辩论上下文
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            辩手回应内容
        """
        debater = self.debaters[debater_name]
        opponent = self.debaters[opponent_name]

        system_prompt = debater.get_system_prompt()

        opponent_view = ""
        for turn in reversed(context.history):
            if turn["speaker"] == opponent_name:
                opponent_view = turn["content"]
                break

        response = debater.skill.generate_response(
            context=context,
            opponent_view=opponent_view,
            system_prompt=system_prompt
        )

        return response

    def create_debate(self, topic: str, debaters: List[str], skills: Optional[List[str]] = None) -> Debate:
        """
        创建辩论（支持双人/多人模式）

        Args:
            topic: 辩论主题
            debaters: 辩手列表，如 ["小明", "小红"] 或 ["小明", "小红", "小李"]
            skills: 辩手策略列表，默认使用 rational

        Returns:
            Debate: 创建的辩论实例
        """
        from .skills import get_skill

        if len(debaters) < 2:
            raise ValueError("辩论至少需要两个辩手")
        
        skills = skills or ["rational"] * len(debaters)
        
        for i, debater_name in enumerate(debaters):
            skill_name = skills[i] if i < len(skills) else "rational"
            self.add_debater(debater_name, skill=get_skill(skill_name))

        debate = Debate(
            id=str(uuid.uuid4())[:8],
            topic=topic,
            status=DebateStatus.PENDING,
            debaters=debaters,
            skills={debaters[i]: skills[i] if i < len(skills) else "rational" for i in range(len(debaters))}
        )

        self.debates[debate.id] = debate
        return debate

    def create_duel_debate(self, topic: str, debater1: str, debater2: str, skill1: str = "rational", skill2: str = "contrarian") -> Debate:
        """
        创建双人辩论（兼容旧API）

        Args:
            topic: 辩论主题
            debater1: 辩手1名称
            debater2: 辩手2名称
            skill1: 辩手1策略
            skill2: 辩手2策略

        Returns:
            Debate: 创建的辩论实例
        """
        return self.create_debate(topic, [debater1, debater2], [skill1, skill2])

    def get_debate(self, debate_id: str) -> Debate:
        """
        获取辩论

        Args:
            debate_id: 辩论ID

        Returns:
            Debate: 辩论实例

        Raises:
            ValueError: 辩论不存在
        """
        if debate_id not in self.debates:
            raise ValueError(f"辩论不存在: {debate_id}")
        return self.debates[debate_id]

    def add_turn(self, debate_id: str, speaker: str, content: str, skill_used: str = ""):
        """
        添加辩论回合

        Args:
            debate_id: 辩论ID
            speaker: 发言者
            content: 内容
            skill_used: 使用的策略
        """
        debate = self.get_debate(debate_id)
        debate.add_turn(speaker, content, skill_used)
        if debate.status == DebateStatus.PENDING:
            debate.status = DebateStatus.IN_PROGRESS

    def complete_debate(self, debate_id: str):
        """
        完成辩论

        Args:
            debate_id: 辩论ID
        """
        debate = self.get_debate(debate_id)
        debate.status = DebateStatus.COMPLETED
        debate.completed_at = datetime.now()
        debate.save(self.output_dir)

    def list_debates(self) -> List[Dict]:
        """列出所有辩论"""
        return [d.to_dict() for d in self.debates.values()]


@dataclass
class DebateContext:
    """辩论上下文"""
    topic: str
    round_num: int
    total_rounds: int
    history: List[Dict]
    current_speaker: str
    opponent_speaker: str

    def to_prompt(self) -> str:
        """转换为提示词"""
        history_text = "\n".join([
            f"{turn['speaker']}：{turn['content']}"
            for turn in self.history[-6:]
        ])

        return f"""辩论主题：{self.topic}

对话历史：
{history_text}

现在是第 {self.round_num}/{self.total_rounds} 轮，请 {self.current_speaker} 继续辩论。"""
