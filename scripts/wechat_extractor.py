#!/usr/bin/env python3
"""
WeChat Data Extractor - 微信数据提取工具

集成 PyWxDump 自动提取和解密微信聊天记录
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime


class WeChatExtractor:
    """微信数据提取器"""

    def __init__(self):
        self.wxdump_available = self._check_pywxdump()

    def _check_pywxdump(self) -> bool:
        """检查 PyWxDump 是否可用"""
        try:
            import pywxdump
            return True
        except ImportError:
            return False

    def install_pywxdump(self):
        """安装 PyWxDump"""
        print("📦 正在安装 PyWxDump...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-U", "pywxdump"
        ])
        self.wxdump_available = True
        print("✅ PyWxDump 安装完成！")

    def get_wechat_info(self) -> Optional[Dict]:
        """获取微信信息"""
        if not self.wxdump_available:
            print("❌ PyWxDump 未安装")
            return None

        try:
            from pywxdump import info

            result = info.run()
            return result
        except Exception as e:
            print(f"❌ 获取微信信息失败: {e}")
            return None

    def decrypt_database(
        self,
        db_key: str,
        db_path: Path,
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """解密微信数据库"""
        if not self.wxdump_available:
            print("❌ PyWxDump 未安装")
            return None

        if output_path is None:
            output_path = Path("data/wechat_decrypted")

        output_path.mkdir(parents=True, exist_ok=True)

        try:
            from pywxdump import decrypt

            print(f"🔓 正在解密数据库: {db_path}")
            decrypt.run(
                key=db_key,
                path=str(db_path),
                out=str(output_path)
            )
            print(f"✅ 解密完成: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ 解密失败: {e}")
            return None

    def export_chat_to_html(
        self,
        wxid: str,
        output_path: Path,
        msg_db: Path,
        micro_db: Optional[Path] = None,
        media_db: Optional[Path] = None
    ) -> Optional[Path]:
        """导出聊天记录为 HTML"""
        if not self.wxdump_available:
            print("❌ PyWxDump 未安装")
            return None

        output_path.mkdir(parents=True, exist_ok=True)

        try:
            from pywxdump import export

            args = {
                "mode": "export",
                "wxid": wxid,
                "output": str(output_path),
                "msg": str(msg_db)
            }

            if micro_db:
                args["micro"] = str(micro_db)
            if media_db:
                args["media"] = str(media_db)

            print(f"📤 正在导出聊天记录...")
            export.run(**args)

            html_file = output_path / f"{wxid}.html"
            if html_file.exists():
                print(f"✅ 导出完成: {html_file}")
                return html_file
            else:
                print("❌ 导出失败：文件未生成")
                return None

        except Exception as e:
            print(f"❌ 导出失败: {e}")
            return None

    def browse_chat(
        self,
        merged_db: Path,
        wid: Optional[Path] = None,
        allow_lan: bool = False
    ):
        """浏览聊天记录（启动 Web 服务）"""
        if not self.wxdump_available:
            print("❌ PyWxDump 未安装")
            return

        try:
            from pywxdump import dbshow

            args = {
                "merge": str(merged_db),
            }

            if wid:
                args["wid"] = str(wid)

            if allow_lan:
                args["online"] = True

            print("🌐 正在启动聊天记录浏览服务...")
            print("📍 访问 http://127.0.0.1:5000 查看聊天记录")
            print("   按 Ctrl+C 停止服务")

            dbshow.run(**args)

        except Exception as e:
            print(f"❌ 启动失败: {e}")

    def get_all_chats(self, db_path: Path) -> List[Dict]:
        """获取所有聊天会话列表"""
        if not self.wxdump_available:
            print("❌ PyWxDump 未安装")
            return []

        try:
            import sqlite3

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT m.StrTalker, m.NickName, COUNT(*) as msg_count
                FROM ChatRoomMember m
                GROUP BY m.StrTalker
                ORDER BY msg_count DESC
            """)

            chats = []
            for row in cursor.fetchall():
                chats.append({
                    "talker": row[0],
                    "nickname": row[1],
                    "msg_count": row[2]
                })

            conn.close()
            return chats

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            return []


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="微信数据提取工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    install_parser = subparsers.add_parser("install", help="安装 PyWxDump")

    info_parser = subparsers.add_parser("info", help="获取微信信息")

    decrypt_parser = subparsers.add_parser("decrypt", help="解密微信数据库")
    decrypt_parser.add_argument("-k", "--key", required=True, help="数据库密钥")
    decrypt_parser.add_argument("-i", "--input", required=True, help="加密数据库路径")
    decrypt_parser.add_argument("-o", "--output", default="data/wechat_decrypted", help="输出路径")

    export_parser = subparsers.add_parser("export", help="导出聊天记录")
    export_parser.add_argument("-u", "--wxid", required=True, help="微信账号")
    export_parser.add_argument("-o", "--output", required=True, help="输出路径")
    export_parser.add_argument("-msg", "--msg-db", required=True, help="MSG.db 路径")
    export_parser.add_argument("-micro", "--micro-db", help="MicroMsg.db 路径")
    export_parser.add_argument("-media", "--media-db", help="MediaMSG.db 路径")

    browse_parser = subparsers.add_parser("browse", help="浏览聊天记录")
    browse_parser.add_argument("-merge", "--merged-db", required=True, help="合并后的数据库路径")
    browse_parser.add_argument("-wid", "--wid", help="微信文件夹路径")
    browse_parser.add_argument("--allow-lan", action="store_true", help="允许局域网访问")

    args = parser.parse_args()

    extractor = WeChatExtractor()

    if args.command == "install":
        extractor.install_pywxdump()

    elif args.command == "info":
        info = extractor.get_wechat_info()
        if info:
            print(json.dumps(info, ensure_ascii=False, indent=2))

    elif args.command == "decrypt":
        extractor.decrypt_database(
            db_key=args.key,
            db_path=Path(args.input),
            output_path=Path(args.output)
        )

    elif args.command == "export":
        extractor.export_chat_to_html(
            wxid=args.wxid,
            output_path=Path(args.output),
            msg_db=Path(args.msg_db),
            micro_db=Path(args.micro_db) if args.micro_db else None,
            media_db=Path(args.media_db) if args.media_db else None
        )

    elif args.command == "browse":
        extractor.browse_chat(
            merged_db=Path(args.merged_db),
            wid=Path(args.wid) if args.wid else None,
            allow_lan=args.allow_lan
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
