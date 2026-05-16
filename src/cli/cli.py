#!/usr/bin/env python3
"""
e-battle CLI - 命令行接口
"""

import argparse
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, os.path.join(str(Path(__file__).parent.parent.parent), 'src'))

from clone.manager import FriendManager


def print_friend_list(manager):
    """打印好友列表"""
    friends = manager.get_friend_list()
    
    if not friends:
        print("暂无好友，请先导入聊天记录")
        return
    
    print("\n📋 好友列表:")
    print("-" * 50)
    for i, friend in enumerate(friends, 1):
        print(f"{i}. {friend.name}")
        print(f"   ├─ 平台: {friend.platform}")
        print(f"   ├─ 消息数: {friend.message_count}")
        print(f"   ├─ 创建时间: {friend.created_at.strftime('%Y-%m-%d %H:%M')}")
        if friend.last_used_at:
            print(f"   └─ 最后使用: {friend.last_used_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"   └─ 最后使用: 从未使用")


def import_friend_cli(manager):
    """导入好友"""
    chat_path = input("请输入聊天记录文件路径: ").strip()
    friend_name = input("请输入好友名称: ").strip()
    platform = input("请输入平台 (wechat/telegram/qq) [默认 wechat]: ").strip() or "wechat"
    
    try:
        chat_path = Path(chat_path)
        if not chat_path.exists():
            print(f"❌ 文件不存在: {chat_path}")
            return
        
        profile = manager.import_friend(chat_path, friend_name, platform)
        print(f"✅ 成功导入好友: {profile.name}")
        
    except Exception as e:
        print(f"❌ 导入失败: {e}")


def delete_friend_cli(manager):
    """删除好友"""
    print_friend_list(manager)
    
    if manager.get_friend_count() == 0:
        return
    
    name = input("\n请输入要删除的好友名称: ").strip()
    
    if not manager.is_friend_exists(name):
        print(f"❌ 好友 '{name}' 不存在")
        return
    
    confirm = input(f"确定要删除 '{name}' 吗？(y/N): ").strip().lower()
    if confirm == 'y':
        manager.delete_friend(name)
        print(f"✅ 好友 '{name}' 已删除")
    else:
        print("取消删除")


def select_friends_cli(manager):
    """选择好友进行对话（支持双人/多人模式）"""
    friends = manager.get_friend_list()
    
    if len(friends) < 2:
        print("❌ 至少需要两个好友才能进行对话")
        return
    
    print("\n📋 当前好友列表:")
    for i, friend in enumerate(friends, 1):
        print(f"{i}. {friend.name}")
    
    # 选择模式
    print("\n🎮 选择Battle模式:")
    print("1. 双人Battle（选择2人）")
    if len(friends) >= 3:
        print("2. 多人Battle（选择3人及以上）")
    
    mode_choice = input("\n请选择模式 [默认: 1]: ").strip() or "1"
    
    if mode_choice == "2" and len(friends) >= 3:
        # 多人模式
        return select_multiplayers_cli(manager, friends)
    else:
        # 双人模式
        return select_duel_cli(manager, friends)


def select_duel_cli(manager, friends):
    """双人Battle选择"""
    print("\n📋 选择第一个好友:")
    for i, friend in enumerate(friends, 1):
        print(f"{i}. {friend.name}")
    
    try:
        idx1 = int(input("输入序号: ")) - 1
        if idx1 < 0 or idx1 >= len(friends):
            print("❌ 无效序号")
            return
        name1 = friends[idx1].name
    except ValueError:
        print("❌ 请输入数字")
        return
    
    print("\n📋 选择第二个好友:")
    available = [f for i, f in enumerate(friends) if i != idx1]
    for i, friend in enumerate(available, 1):
        print(f"{i}. {friend.name}")
    
    try:
        idx2 = int(input("输入序号: ")) - 1
        if idx2 < 0 or idx2 >= len(available):
            print("❌ 无效序号")
            return
        name2 = available[idx2].name
    except ValueError:
        print("❌ 请输入数字")
        return
    
    print(f"\n⚔️ 【双人Battle】{name1} vs {name2}")
    print("✅ 可以开始辩论了！")


def select_multiplayers_cli(manager, friends):
    """多人Battle选择"""
    print("\n🎭 多人Battle模式")
    print("请选择参赛者（输入序号，用空格分隔，输入q完成选择）:")
    
    selected = []
    while True:
        print("\n📋 当前好友列表:")
        for i, friend in enumerate(friends, 1):
            status = "✓ 已选择" if friend.name in selected else ""
            print(f"{i}. {friend.name} {status}")
        
        if len(selected) >= 3:
            print("\n💡 已选择3人及以上，可以开始Battle！")
            confirm = input("输入y确认开始，输入其他继续添加: ").strip().lower()
            if confirm == 'y':
                break
        
        print(f"\n已选择: {', '.join(selected) if selected else '暂无'}")
        choice = input("\n输入序号添加参赛者（或q完成: ").strip()
        
        if choice.lower() == 'q':
            if len(selected) < 2:
                print("❌ 至少需要2人！")
                continue
            break
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(friends):
                print("❌ 无效序号")
                continue
            
            name = friends[idx].name
            if name in selected:
                print(f"❌ {name} 已经在列表中")
            else:
                selected.append(name)
                print(f"✅ 添加了 {name}")
        except ValueError:
            print("❌ 请输入数字")
    
    print(f"\n⚔️ 【多人Battle】{' vs '.join(selected)}")
    print(f"👥 共 {len(selected)} 人参赛")
    print("✅ 可以开始Battle了！")


def create_sample_friends_cli(manager):
    """创建示例好友"""
    manager.create_sample_friends()
    print(f"✅ 示例好友创建完成，当前好友数: {manager.get_friend_count()}")


def main():
    parser = argparse.ArgumentParser(description="e-battle - AI好友辩论系统")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list - 列出好友
    subparsers.add_parser('list', help='列出所有好友')
    
    # import - 导入好友
    import_parser = subparsers.add_parser('import', help='导入聊天记录创建好友')
    import_parser.add_argument('chat_path', nargs='?', help='聊天记录文件路径')
    import_parser.add_argument('name', nargs='?', help='好友名称')
    import_parser.add_argument('--platform', default='wechat', help='平台类型')
    
    # delete - 删除好友
    delete_parser = subparsers.add_parser('delete', help='删除好友')
    delete_parser.add_argument('name', nargs='?', help='好友名称')
    
    # select - 选择好友
    subparsers.add_parser('select', help='选择好友进行对话')
    
    # sample - 创建示例好友
    subparsers.add_parser('sample', help='创建示例好友')
    
    args = parser.parse_args()
    
    manager = FriendManager()
    
    if args.command == 'list':
        print_friend_list(manager)
    
    elif args.command == 'import':
        if args.chat_path and args.name:
            try:
                manager.import_friend(Path(args.chat_path), args.name, args.platform)
                print(f"✅ 成功导入好友: {args.name}")
            except Exception as e:
                print(f"❌ 导入失败: {e}")
        else:
            import_friend_cli(manager)
    
    elif args.command == 'delete':
        if args.name:
            if manager.is_friend_exists(args.name):
                manager.delete_friend(args.name)
                print(f"✅ 好友 '{args.name}' 已删除")
            else:
                print(f"❌ 好友 '{args.name}' 不存在")
        else:
            delete_friend_cli(manager)
    
    elif args.command == 'select':
        select_friends_cli(manager)
    
    elif args.command == 'sample':
        create_sample_friends_cli(manager)
    
    else:
        # 交互式模式
        print("=" * 50)
        print("     e-battle CLI")
        print("=" * 50)
        print("1. 列出好友")
        print("2. 导入好友")
        print("3. 删除好友")
        print("4. 选择好友进行对话")
        print("5. 创建示例好友")
        print("0. 退出")
        print("=" * 50)
        
        while True:
            try:
                choice = input("\n请输入选择: ")
                
                if choice == '1':
                    print_friend_list(manager)
                elif choice == '2':
                    import_friend_cli(manager)
                elif choice == '3':
                    delete_friend_cli(manager)
                elif choice == '4':
                    select_friends_cli(manager)
                elif choice == '5':
                    create_sample_friends_cli(manager)
                elif choice == '0':
                    print("👋 再见！")
                    break
                else:
                    print("❌ 无效选择，请重新输入")
            except KeyboardInterrupt:
                print("\n👋 再见！")
                break


if __name__ == '__main__':
    main()