# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

current_dir = Path(__file__).parent
src_dir = current_dir / "src"
web_dir = src_dir / "web"
templates_dir = web_dir / "templates"

a = Analysis(
    [str(src_dir / "launcher.py")],
    pathex=[str(current_dir)],
    binaries=[],
    datas=[
        (str(templates_dir), "src/web/templates"),
        ("README.md", "."),
        ("README_zh.md", "."),
        ("config", "config"),
    ],
    hiddenimports=[
        "flask",
        "flask_cors",
        "bs4",
        "lxml",
        "PIL._imagingtk",
        "PIL._tkinter_finder",
        "pandas",
        "numpy",
        "yaml",
        "tkinter",
        "tkinter.ttk",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "scipy",
        "sklearn",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="FriendBattle",
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
