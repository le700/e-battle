#!/usr/bin/env python3
"""
FriendBattle - 内置微信聊天记录导出工具
无需安装其他软件，一键导出聊天记录
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

try:
    import win32api
    import win32con
    import win32gui
    import win32process
    HAS_WINDOWS_API = True
except ImportError:
    HAS_WINDOWS_API = False

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class WeChatExporter:
    def __init__(self):
        self.wechat_path = self._find_wechat_path()
        self.output_dir = Path("data/chatlogs")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _find_wechat_path(self):
        """查找微信安装路径"""
        common_paths = [
            Path(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Tencent\\WeChat'),
            Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Tencent\\WeChat'),
            Path(os.environ.get('USERPROFILE'), 'AppData\\Roaming\\Tencent\\WeChat'),
        ]
        
        for path in common_paths:
            if path.exists():
                return path
        return None

    def is_wechat_running(self):
        """检查微信是否正在运行"""
        if not HAS_PSUTIL:
            return False
            
        for proc in psutil.process_iter(['name']):
            try:
                if proc.name().lower() == 'wechat.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False

    def export_chat_history(self, friend_name=None):
        """
        导出微信聊天记录
        
        参数:
            friend_name: 好友名称（可选），不指定则导出所有好友
            
        返回:
            list: 导出的文件路径列表
        """
        exported_files = []
        
        if not self.wechat_path:
            print("❌ 未找到微信安装路径")
            return exported_files

        print(f"📱 微信路径: {self.wechat_path}")

        db_path = self.wechat_path / "WeChat Files"
        
        if not db_path.exists():
            print("❌ 未找到微信数据目录")
            return exported_files

        print("📤 开始导出聊天记录...")

        for account_dir in db_path.iterdir():
            if not account_dir.is_dir():
                continue
                
            msg_db = account_dir / "Msg" / "Msg.db"
            if msg_db.exists():
                export_path = self.output_dir / f"{account_dir.name}_messages.json"
                try:
                    self._export_db_to_json(msg_db, export_path, friend_name)
                    exported_files.append(str(export_path))
                    print(f"✅ 导出: {export_path}")
                except Exception as e:
                    print(f"❌ 导出失败 {account_dir.name}: {e}")

        return exported_files

    def _export_db_to_json(self, db_path, output_path, friend_name=None):
        """将数据库导出为 JSON"""
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            query = """
                SELECT Message, CreateTime, Talker, Type 
                FROM Message 
                ORDER BY CreateTime ASC
            """
            
            cursor.execute(query)
            messages = []
            
            for row in cursor.fetchall():
                msg_text, create_time, talker, msg_type = row
                
                if friend_name and friend_name != talker:
                    continue
                    
                messages.append({
                    "text": msg_text,
                    "time": datetime.fromtimestamp(create_time).isoformat(),
                    "talker": talker,
                    "type": msg_type
                })
            
            conn.close()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
                
        except ImportError:
            self._fallback_export(db_path, output_path)
        except Exception as e:
            raise e

    def _fallback_export(self, db_path, output_path):
        """备用导出方法"""
        messages = [{
            "text": "微信聊天记录（请手动导出）",
            "time": datetime.now().isoformat(),
            "talker": "Friend",
            "type": 1
        }]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    def generate_sample_data(self):
        """生成示例聊天数据用于测试"""
        sample_data = [{
            "text": "今天天气真好啊！",
            "time": "2024-01-15T10:00:00",
            "talker": "小明",
            "type": 1
        }, {
            "text": "是啊，适合出去玩",
            "time": "2024-01-15T10:01:00",
            "talker": "小红",
            "type": 1
        }, {
            "text": "我们去爬山吧！",
            "time": "2024-01-15T10:02:00",
            "talker": "小明",
            "type": 1
        }, {
            "text": "好啊，我带点零食",
            "time": "2024-01-15T10:03:00",
            "talker": "小红",
            "type": 1
        }]
        
        output_path = self.output_dir / "sample_messages.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
            
        return str(output_path)


class AIProvider:
    """
    AI 服务提供商管理器
    支持多种 AI API
    """
    
    def __init__(self, provider="openai", api_key=None, base_url=None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.base_url = base_url
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化 AI 客户端"""
        try:
            if self.provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url or "https://api.openai.com/v1"
                )
            elif self.provider == "claude":
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
            elif self.provider == "deepseek":
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            elif self.provider == "zhipu":
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://open.bigmodel.cn/api/paas/v4"
                )
            elif self.provider == "local":
                self.client = self._init_local_model()
            else:
                raise ValueError(f"不支持的 AI 提供商: {self.provider}")
        except ImportError as e:
            print(f"⚠️ 缺少依赖: {e}")
            self.client = None

    def _init_local_model(self):
        """初始化本地模型"""
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            model_name = "Qwen/Qwen2-0.5B-Chat"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            return pipeline("text-generation", model=model, tokenizer=tokenizer)
        except Exception as e:
            print(f"⚠️ 本地模型加载失败: {e}")
            return None

    def generate(self, prompt, model=None, max_tokens=512):
        """生成文本"""
        if not self.client:
            return "❌ AI 客户端未初始化"

        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=model or "gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "claude":
                response = self.client.messages.create(
                    model=model or "claude-3-sonnet-20240229",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif self.provider == "gemini":
                model = self.client.GenerativeModel(model or "gemini-pro")
                response = model.generate_content(prompt)
                return response.text
            
            elif self.provider == "deepseek":
                response = self.client.chat.completions.create(
                    model=model or "deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "zhipu":
                response = self.client.chat.completions.create(
                    model=model or "glm-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif self.provider == "local":
                if hasattr(self.client, '__call__'):
                    result = self.client(prompt, max_length=max_tokens)
                    return result[0]['generated_text']
                return "⚠️ 本地模型未正确加载"
            
            else:
                return f"❌ 不支持的提供商: {self.provider}"
                
        except Exception as e:
            return f"❌ 生成失败: {str(e)}"

    @staticmethod
    def list_providers():
        """列出支持的 AI 提供商"""
        return [
            {"name": "openai", "label": "OpenAI", "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]},
            {"name": "claude", "label": "Claude", "models": ["claude-3-sonnet", "claude-3-opus"]},
            {"name": "gemini", "label": "Gemini", "models": ["gemini-pro", "gemini-1.5-pro"]},
            {"name": "deepseek", "label": "DeepSeek", "models": ["deepseek-chat"]},
            {"name": "zhipu", "label": "智谱AI", "models": ["glm-4", "glm-4v"]},
            {"name": "local", "label": "本地模型", "models": ["Qwen2-0.5B", "Llama-3-8B"]},
        ]


def main():
    print("🎭 FriendBattle - 微信导出工具")
    print("=" * 40)
    
    exporter = WeChatExporter()
    
    if exporter.is_wechat_running():
        print("⚠️ 检测到微信正在运行，请先关闭微信")
        return
    
    print("\n📤 开始导出微信聊天记录...")
    exported = exporter.export_chat_history()
    
    if exported:
        print(f"\n✅ 成功导出 {len(exported)} 个文件")
        for f in exported:
            print(f"   - {f}")
    else:
        print("\n❌ 未找到聊天记录，生成示例数据...")
        sample = exporter.generate_sample_data()
        print(f"✅ 已生成示例数据: {sample}")
    
    print("\n🎉 导出完成！")
    print("请打开 FriendBattle Web 界面上传聊天记录")


if __name__ == "__main__":
    main()
