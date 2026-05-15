#!/usr/bin/env python3
"""
FriendBattle TUI - 终端用户界面
使用 Rich 和 Textual 创建美观的终端界面
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, os.path.join(str(Path(__file__).parent.parent.parent), 'src'))

from clone.manager import FriendManager


def print_header():
    """打印头部"""
    print("\n" + "=" * 70)
    print("                    FriendBattle")
    print("               AI 好友辩论系统")
    print("=" * 70)


def print_menu():
    """打印菜单"""
    print("\n📱 主菜单")
    print("-" * 40)
    print("  1. 📋 查看好友列表")
    print("  2. 📤 导入聊天记录")
    print("  3. 🗑️ 删除好友")
    print("  4. ⚔️ 选择好友辩论")
    print("  5. 🎨 创建示例好友")
    print("  0. 👋 退出")
    print("-" * 40)


def display_friends(manager):
    """显示好友列表"""
    friends = manager.get_friend_list()
    
    if not friends:
        print("\n📭 暂无好友")
        print("  请先导入聊天记录创建好友")
        return
    
    print("\n📋 好友列表")
    print("-" * 60)
    print(f" {'序号':^4} | {'名称':^10} | {'平台':^10} | {'消息数':^8} | {'创建时间':^20}")
    print("-" * 60)
    
    for i, friend in enumerate(friends, 1):
        created = friend.created_at.strftime('%Y-%m-%d %H:%M')
        print(f" {i:^4} | {friend.name:^10} | {friend.platform:^10} | {friend.message_count:^8} | {created:^20}")
    
    print("-" * 60)
    print(f" 共 {len(friends)} 位好友")


def import_friend_tui(manager):
    """导入好友"""
    print("\n📤 导入聊天记录")
    print("-" * 40)
    
    chat_path = input("  聊天记录文件路径: ").strip()
    if not chat_path:
        print("  ❌ 路径不能为空")
        return
    
    path = Path(chat_path)
    if not path.exists():
        print(f"  ❌ 文件不存在: {chat_path}")
        return
    
    name = input("  好友名称: ").strip()
    if not name:
        print("  ❌ 名称不能为空")
        return
    
    platform = input("  平台 (wechat/telegram/qq) [wechat]: ").strip() or "wechat"
    
    print(f"\n  正在分析 {name} 的聊天记录...")
    try:
        profile = manager.import_friend(path, name, platform)
        print(f"  ✅ 成功导入好友: {profile.name}")
        print(f"     - 消息数量: {manager.friends[name].message_count}")
        print(f"     - 语言风格: {profile.language_style}")
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")


def delete_friend_tui(manager):
    """删除好友"""
    friends = manager.get_friend_list()
    
    if not friends:
        print("\n📭 暂无好友")
        return
    
    display_friends(manager)
    
    print("\n🗑️ 删除好友")
    print("-" * 40)
    
    try:
        idx = int(input("  输入要删除的好友序号: ")) - 1
        if idx < 0 or idx >= len(friends):
            print("  ❌ 无效序号")
            return
        
        friend = friends[idx]
        confirm = input(f"  确定删除 '{friend.name}' 吗？(y/N): ").strip().lower()
        
        if confirm == 'y':
            manager.delete_friend(friend.name)
            print(f"  ✅ 好友 '{friend.name}' 已删除")
        else:
            print("  ✅ 取消删除")
            
    except ValueError:
        print("  ❌ 请输入数字")


def select_friends_tui(manager):
    """选择好友辩论"""
    friends = manager.get_friend_list()
    
    if len(friends) < 2:
        print("\n❌ 至少需要 2 位好友才能开始辩论")
        print(f"   当前只有 {len(friends)} 位好友")
        return
    
    display_friends(manager)
    
    print("\n⚔️ 选择辩论选手")
    print("-" * 40)
    
    try:
        idx1 = int(input("  选择第一位选手 (序号): ")) - 1
        if idx1 < 0 or idx1 >= len(friends):
            print("  ❌ 无效序号")
            return
        
        friend1 = friends[idx1]
        
        # 显示剩余好友
        print(f"\n  已选择: {friend1.name}")
        print("  -------------------")
        print(f" {'序号':^4} | {'名称':^10}")
        print("  -------------------")
        
        available = [f for f in friends if f.name != friend1.name]
        for i, friend in enumerate(available, 1):
            print(f" {i:^4} | {friend.name:^10}")
        
        idx2 = int(input("\n  选择第二位选手 (序号): ")) - 1
        if idx2 < 0 or idx2 >= len(available):
            print("  ❌ 无效序号")
            return
        
        friend2 = available[idx2]
        
        print(f"\n  ✅ 辩论选手已选择:")
        print(f"     {friend1.name} VS {friend2.name}")
        print(f"\n  🎮 可以开始辩论了！")
        
    except ValueError:
        print("  ❌ 请输入数字")


def create_sample_friends_tui(manager):
    """创建示例好友"""
    print("\n🎨 创建示例好友")
    print("-" * 40)
    
    print("  正在创建示例好友...")
    manager.create_sample_friends()
    
    print(f"  ✅ 示例好友创建完成")
    print(f"     当前好友数: {manager.get_friend_count()}")


def main():
    manager = FriendManager()
    
    while True:
        print_header()
        print_menu()
        
        try:
            choice = input("\n请输入选择 [0-5]: ").strip()
            
            if choice == '1':
                display_friends(manager)
            elif choice == '2':
                import_friend_tui(manager)
            elif choice == '3':
                delete_friend_tui(manager)
            elif choice == '4':
                select_friends_tui(manager)
            elif choice == '5':
                create_sample_friends_tui(manager)
            elif choice == '0':
                print("\n👋 感谢使用 FriendBattle!")
                print("   再见！")
                break
            else:
                print("\n❌ 无效选择，请输入 0-5")
                
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用 FriendBattle!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


if __name__ == '__main__':
    main()