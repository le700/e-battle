#!/usr/bin/env python3
"""
FriendBattle - AI好友辩论系统
主入口脚本

支持三种界面模式：
1. CLI - 命令行接口
2. TUI - 终端用户界面
3. GUI - Web图形界面
"""

import sys
from pathlib import Path


def run_cli():
    """运行CLI模式"""
    from src.cli.cli import main as cli_main
    cli_main()


def run_tui():
    """运行TUI模式"""
    from src.tui.tui import main as tui_main
    tui_main()


def run_gui():
    """运行Web GUI模式"""
    from src.web.app import main as gui_main
    gui_main()


def main():
    # 检查是否指定了模式
    if len(sys.argv) > 1 and sys.argv[1] in ['cli', 'tui', 'gui']:
        mode = sys.argv[1]
        
        if mode == 'cli':
            # 传递所有剩余参数给CLI（去掉 'cli' 本身）
            sys.argv = ['friendbattle-cli'] + sys.argv[2:]
            run_cli()
        elif mode == 'tui':
            run_tui()
        elif mode == 'gui':
            run_gui()
        return
    
    # 否则显示选择菜单
    print("=" * 60)
    print("           FriendBattle")
    print("        AI 好友辩论系统")
    print("=" * 60)
    print()
    print("请选择运行模式:")
    print("-" * 30)
    print("  1. CLI   - 命令行接口")
    print("  2. TUI   - 终端用户界面")
    print("  3. GUI   - Web图形界面")
    print("  0. 退出")
    print("-" * 30)
    
    while True:
        try:
            choice = input("\n输入选择 [0-3]: ").strip()
            
            if choice == '1':
                print("\n🚀 启动 CLI 模式...")
                run_cli()
                break
            elif choice == '2':
                print("\n🚀 启动 TUI 模式...")
                run_tui()
                break
            elif choice == '3':
                print("\n🚀 启动 GUI 模式...")
                run_gui()
                break
            elif choice == '0':
                print("\n👋 再见！")
                break
            else:
                print("❌ 无效选择，请输入 0-3")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break


if __name__ == '__main__':
    main()
