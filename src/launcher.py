#!/usr/bin/env python3
"""
FriendBattle Launcher - Windows 启动器

提供一个友好的 GUI 界面来启动 FriendBattle
"""

import os
import sys
import subprocess
import threading
import webbrowser
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("Tkinter not available, running in console mode")
    sys.exit(1)


class FriendBattleLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("FriendBattle - AI好友辩论 Battle")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        self.process = None
        self.server_running = False

        self.create_widgets()

    def create_widgets(self):
        # Logo/Title
        title_frame = ttk.Frame(self.root, padding="20")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="🎭 FriendBattle",
            font=("Arial", 24, "bold")
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="让你的微信好友 AI 克隆人互相对战！",
            font=("Arial", 12),
            foreground="#666"
        )
        subtitle_label.pack(pady=(5, 0))

        # Status
        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(
            status_frame,
            text="🟢 准备就绪",
            font=("Arial", 11)
        )
        self.status_label.pack()

        # Main Button
        button_frame = ttk.Frame(self.root, padding="20")
        button_frame.pack(fill=tk.X)

        self.start_button = ttk.Button(
            button_frame,
            text="🚀 启动 FriendBattle",
            command=self.toggle_server,
            style="Accent.TButton"
        )
        self.start_button.pack(fill=tk.X, ipady=10)

        # Port Info
        port_frame = ttk.Frame(self.root, padding="10")
        port_frame.pack(fill=tk.X)

        ttk.Label(port_frame, text="访问地址:").pack(anchor=tk.W)
        self.url_label = ttk.Label(
            port_frame,
            text="http://localhost:3000",
            foreground="#007bff",
            cursor="hand2"
        )
        self.url_label.pack(anchor=tk.W)
        self.url_label.bind("<Button-1>", self.open_browser)

        # Log Area
        log_frame = ttk.Frame(self.root, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(log_frame, text="运行日志:").pack(anchor=tk.W)

        self.log_text = tk.Text(
            log_frame,
            height=15,
            width=50,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Footer
        footer_frame = ttk.Frame(self.root, padding="10")
        footer_frame.pack(fill=tk.X)

        ttk.Label(
            footer_frame,
            text="FriendBattle v1.0.0 | 让好友替你吵架！",
            font=("Arial", 10),
            foreground="#888"
        ).pack()

        # Style
        style = ttk.Style()
        style.configure(
            "Accent.TButton",
            font=("Arial", 12, "bold"),
            padding=10
        )

    def toggle_server(self):
        if self.server_running:
            self.stop_server()
        else:
            self.start_server()

    def start_server(self):
        self.status_label.config(text="🔄 启动中...")
        self.start_button.config(text="⏹️ 停止 FriendBattle")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        def run_server():
            try:
                self.process = subprocess.Popen(
                    [sys.executable, "-m", "src.web.app"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(Path(__file__).parent)
                )

                self.server_running = True
                self.status_label.config(text="✅ 运行中")
                self.log("服务器已启动")
                self.log("访问地址: http://localhost:3000")

                while self.server_running:
                    line = self.process.stdout.readline()
                    if line:
                        self.log(line.strip())

            except Exception as e:
                self.log(f"❌ 启动失败: {e}")
                self.status_label.config(text="❌ 启动失败")
                self.start_button.config(text="🚀 启动 FriendBattle")
                self.server_running = False

        threading.Thread(target=run_server, daemon=True).start()

    def stop_server(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

        self.server_running = False
        self.status_label.config(text="🟢 已停止")
        self.start_button.config(text="🚀 启动 FriendBattle")
        self.log("服务器已停止")

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def open_browser(self, event):
        if self.server_running:
            webbrowser.open("http://localhost:3000")
        else:
            messagebox.showinfo("提示", "请先启动服务器")

    def on_closing(self):
        if self.server_running:
            self.stop_server()
        self.root.destroy()


def main():
    root = tk.Tk()
    launcher = FriendBattleLauncher(root)
    root.protocol("WM_DELETE_WINDOW", launcher.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
