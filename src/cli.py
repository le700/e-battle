#!/usr/bin/env python3
"""
FriendDebate CLI - 命令行界面

提供命令行工具来管理辩论和角色
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.clone import FriendCloner, AvatarStorage
from src.debate import DebateEngine, get_skill
from src.debate.formatters import ConsoleFormatter


def create_avatar(args):
    """创建角色"""
    print(f"📋 正在分析聊天记录: {args.chat_log}")

    cloner = FriendCloner(platform=args.platform)
    profile = cloner.create_profile(
        chat_log_path=Path(args.chat_log),
        name=args.name,
        output_dir=Path(args.output_dir)
    )

    storage = AvatarStorage(Path(args.output_dir))
    avatar_path = storage.save_avatar(profile)

    print(f"✅ 角色创建成功！")
    print(f"   名称: {profile.name}")
    print(f"   语言风格: {profile.language_style}")
    print(f"   性格特点: {', '.join(profile.personality_traits)}")
    print(f"   保存位置: {avatar_path}")


def list_avatars(args):
    """列出角色"""
    storage = AvatarStorage(Path(args.data_dir))
    avatars = storage.list_avatars()

    if not avatars:
        print("❌ 还没有创建任何角色")
        return

    print(f"📋 共 {len(avatars)} 个角色:\n")
    for avatar in avatars:
        print(f"  👤 {avatar['name']} ({avatar['id']})")
        print(f"     路径: {avatar['path']}")
        print()


def start_debate(args):
    """开始辩论"""
    storage = AvatarStorage(Path(args.data_dir))

    profile1 = storage.load_avatar(args.debater1)
    profile2 = storage.load_avatar(args.debater2)

    if not profile1:
        print(f"❌ 角色 {args.debater1} 不存在")
        return
    if not profile2:
        print(f"❌ 角色 {args.debater2} 不存在")
        return

    engine = DebateEngine(output_dir=Path(args.data_dir) / "debates")

    engine.add_debater(
        name=profile1["name"],
        profile_data=profile1,
        skill=get_skill(args.skill1)()
    )

    engine.add_debater(
        name=profile2["name"],
        profile_data=profile2,
        skill=get_skill(args.skill2)()
    )

    debate = engine.start(
        topic=args.topic,
        rounds=args.rounds,
        max_tokens=args.max_tokens,
        temperature=args.temperature
    )

    formatter = ConsoleFormatter()
    print(formatter.format(debate))


def main():
    parser = argparse.ArgumentParser(
        description="FriendDebate CLI - AI好友辩论系统",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    create_parser = subparsers.add_parser("create", help="创建新角色")
    create_parser.add_argument("--chat-log", required=True, help="聊天记录路径")
    create_parser.add_argument("--name", required=True, help="角色名称")
    create_parser.add_argument("--platform", default="telegram", help="平台类型")
    create_parser.add_argument("--output-dir", default="data", help="输出目录")
    create_parser.set_defaults(func=create_avatar)

    list_parser = subparsers.add_parser("list", help="列出所有角色")
    list_parser.add_argument("--data-dir", default="data", help="数据目录")
    list_parser.set_defaults(func=list_avatars)

    debate_parser = subparsers.add_parser("debate", help="开始辩论")
    debate_parser.add_argument("--debater1", required=True, help="正方角色ID")
    debate_parser.add_argument("--debater2", required=True, help="反方角色ID")
    debate_parser.add_argument("--topic", required=True, help="辩论主题")
    debate_parser.add_argument("--rounds", type=int, default=5, help="辩论回合数")
    debate_parser.add_argument("--skill1", default="contrarian", help="正方策略")
    debate_parser.add_argument("--skill2", default="rational", help="反方策略")
    debate_parser.add_argument("--max-tokens", type=int, default=300, help="最大token数")
    debate_parser.add_argument("--temperature", type=float, default=0.8, help="温度参数")
    debate_parser.add_argument("--data-dir", default="data", help="数据目录")
    debate_parser.set_defaults(func=start_debate)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
