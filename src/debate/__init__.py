"""
Debate - AI辩论引擎模块

支持多种辩论策略的AI辩论系统
"""

from .engine import DebateEngine, Debate, DebateTurn
from .skills import (
    BaseSkill,
    ContrarianSkill,
    RationalSkill,
    HumorousSkill,
    AggressiveSkill,
    DiplomaticSkill,
    SarcasticSkill,
    get_skill,
)
from .formatters import DebateFormatter, ConsoleFormatter, JSONFormatter

__all__ = [
    "DebateEngine",
    "Debate",
    "DebateTurn",
    "BaseSkill",
    "ContrarianSkill",
    "RationalSkill",
    "HumorousSkill",
    "AggressiveSkill",
    "DiplomaticSkill",
    "SarcasticSkill",
    "get_skill",
    "DebateFormatter",
    "ConsoleFormatter",
    "JSONFormatter",
]
