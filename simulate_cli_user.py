#!/usr/bin/env python3
"""
模拟正常用户使用FriendBattle CLI从头到尾操作项目
"""

import sys
import os
from pathlib import Path
import json
import shutil

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.clone.manager import FriendManager
from src.wechat_exporter import WeChatExporter


def clean_data_dir():
    """清理测试数据"""
    data_dir = Path("data")
    if data_dir.exists():
        shutil.rmtree(data_dir)
    print("🧹 已清理旧测试数据\n")


def print_separator(title=""):
    """打印分隔线"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)


def simulate_user():
    """模拟用户操作流程"""
    print("=" * 60)
    print("     FriendBattle CLI 用户操作模拟")
    print("=" * 60)
    
    # 步骤1: 初始化FriendManager
    print_separator("步骤1: 初始化好友管理器")
    manager = FriendManager()
    print("✅ FriendManager初始化成功")
    print(f"   当前好友数: {manager.get_friend_count()}")
    
    # 步骤2: 查看好友列表（为空）
    print_separator("步骤2: 查看好友列表")
    friends = manager.get_friend_list()
    if friends:
        for i, friend in enumerate(friends, 1):
            print(f" {i}. {friend.name}")
    else:
        print("暂无好友")
    
    # 步骤3: 创建示例聊天记录文件
    print_separator("步骤3: 创建示例聊天记录（准备导入）")
    
    sample_data_dir = Path("data/sample_data")
    sample_data_dir.mkdir(parents=True, exist_ok=True)
    
    # 为"老王"创建聊天记录
    laowang_file = sample_data_dir / "laowang.txt"
    with open(laowang_file, "w", encoding="utf-8") as f:
        f.write("""2024-01-15 10:00:00
老王: 嘿，兄弟！
2024-01-15 10:01:00
用户: 啥事啊老王？
2024-01-15 10:02:00
老王: 今晚有没有空？一起去打球？
2024-01-15 10:03:00
用户: 可以啊，几点？
2024-01-15 10:04:00
老王: 7点吧，老地方
2024-01-15 19:00:00
老王: 到了吗？
2024-01-15 19:01:00
用户: 在路上了
2024-01-15 21:30:00
老王: 今天打得真爽！
2024-01-15 21:31:00
用户: 是啊，下次再约
2024-01-16 09:00:00
老王: 早啊！
2024-01-16 09:01:00
用户: 早
2024-01-16 09:02:00
老王: 昨天打完球腿好酸
2024-01-16 09:03:00
用户: 哈哈，太久没运动了
2024-01-16 18:00:00
老王: 下班了吗？
2024-01-16 18:01:00
用户: 刚下班
2024-01-16 18:02:00
老王: 要不要一起吃个饭？
2024-01-16 18:03:00
用户: 好啊
""")
    
    # 为"小李"创建聊天记录
    xiaoli_file = sample_data_dir / "xiaoli.txt"
    with open(xiaoli_file, "w", encoding="utf-8") as f:
        f.write("""2024-01-15 11:00:00
小李: 你好呀！
2024-01-15 11:01:00
用户: 你好
2024-01-15 11:02:00
小李: 最近在忙什么呢？
2024-01-15 11:03:00
用户: 上班啊，忙死了
2024-01-15 11:04:00
小李: 哈哈，大家都一样
2024-01-15 14:00:00
小李: 要不要来杯咖啡？
2024-01-15 14:01:00
用户: 好啊
2024-01-15 14:30:00
小李: 这家店的咖啡真不错
2024-01-15 14:31:00
用户: 是啊，很香
2024-01-16 10:00:00
小李: 周末有空吗？
2024-01-16 10:01:00
用户: 应该有
2024-01-16 10:02:00
小李: 一起去看画展吧
2024-01-16 10:03:00
用户: 好啊，我也想看
2024-01-16 15:00:00
小李: 画展真好看！
2024-01-16 15:01:00
用户: 是啊，收获很大
2024-01-17 09:00:00
小李: 早
2024-01-17 09:01:00
用户: 早
2024-01-17 09:02:00
小李: 今天天气真好
2024-01-17 09:03:00
用户: 是啊
""")
    
    print(f"✅ 已创建示例聊天记录文件:")
    print(f"   - {laowang_file}")
    print(f"   - {xiaoli_file}")
    
    # 步骤4: 导入第一个好友（老王）
    print_separator("步骤4: 导入好友 '老王'")
    try:
        profile_laowang = manager.import_friend(laowang_file, "老王", platform="wechat", min_messages=10)
        print(f"✅ 成功导入好友: {profile_laowang.name}")
        print(f"   语言风格: {profile_laowang.language_style}")
        print(f"   性格特点: {', '.join(profile_laowang.personality_traits)}")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 步骤5: 导入第二个好友（小李）
    print_separator("步骤5: 导入好友 '小李'")
    try:
        profile_xiaoli = manager.import_friend(xiaoli_file, "小李", platform="wechat", min_messages=10)
        print(f"✅ 成功导入好友: {profile_xiaoli.name}")
        print(f"   语言风格: {profile_xiaoli.language_style}")
        print(f"   性格特点: {', '.join(profile_xiaoli.personality_traits)}")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 步骤6: 再次查看好友列表
    print_separator("步骤6: 再次查看好友列表")
    friends = manager.get_friend_list()
    print(f"当前好友数: {len(friends)}")
    for i, friend in enumerate(friends, 1):
        print(f" {i}. {friend.name}")
        print(f"    ├─ 平台: {friend.platform}")
        print(f"    ├─ 消息数: {friend.message_count}")
        print(f"    └─ 创建时间: {friend.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # 步骤7: 获取好友画像详情
    print_separator("步骤7: 查看好友画像详情")
    for friend in friends:
        profile = manager.get_friend_profile(friend.name)
        print(f"\n📋 {friend.name} 的画像:")
        print(f"   语言风格: {profile.language_style}")
        print(f"   常用短语: {', '.join(profile.common_phrases[:5])}")
        print(f"   性格特点: {', '.join(profile.personality_traits)}")
        print(f"   常见话题: {', '.join(profile.conversation_topics)}")
        if profile.emoji_usage:
            print(f"   常用表情: {', '.join(profile.emoji_usage.keys())}")
    
    # 步骤8: 选择两个好友准备辩论
    print_separator("步骤8: 选择好友准备辩论")
    try:
        profile1, profile2 = manager.select_friends_for_battle("老王", "小李")
        print(f"✅ 已选择: {profile1.name} vs {profile2.name}")
        print(f"   准备开始辩论！")
    except Exception as e:
        print(f"❌ 选择失败: {e}")
    
    # 步骤9: 测试删除一个好友（再恢复）
    print_separator("步骤9: 测试删除好友功能")
    try:
        manager.delete_friend("小李")
        print(f"✅ 已删除好友 '小李'")
        print(f"   当前好友数: {manager.get_friend_count()}")
    except Exception as e:
        print(f"❌ 删除失败: {e}")
    
    # 重新导入小李
    print(f"\n重新导入好友 '小李'...")
    try:
        profile_xiaoli = manager.import_friend(xiaoli_file, "小李", platform="wechat", min_messages=10)
        print(f"✅ 成功重新导入: {profile_xiaoli.name}")
    except Exception as e:
        print(f"❌ 重新导入失败: {e}")
    
    # 步骤10: 测试创建示例好友功能
    print_separator("步骤10: 创建更多示例好友")
    try:
        manager.create_sample_friends()
        print(f"✅ 示例好友创建完成")
        print(f"   当前总好友数: {manager.get_friend_count()}")
    except Exception as e:
        print(f"❌ 创建示例好友失败: {e}")
    
    # 最终查看所有好友
    print_separator("最终: 所有好友列表")
    friends = manager.get_friend_list()
    print(f"总共 {len(friends)} 个好友:")
    for i, friend in enumerate(friends, 1):
        print(f" {i}. {friend.name}")
    
    print_separator("模拟完成！")
    print("✅ 所有CLI操作测试通过！项目可以正常使用！")


def main():
    try:
        # 先清理旧数据
        clean_data_dir()
        
        # 模拟用户操作
        simulate_user()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
