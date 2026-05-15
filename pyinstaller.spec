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
        (str(src_dir / "clone"), "src/clone"),
        (str(src_dir / "debate"), "src/debate"),
        (str(src_dir / "share"), "src/share"),
        (str(src_dir / "web"), "src/web"),
        ("README.md", "."),
    ],
    hiddenimports=[
        "flask",
        "flask_cors",
        "transformers",
        "torch",
        "accelerate",
        "peft",
        "sentencepiece",
        "beautifulsoup4",
        "lxml",
        "PIL",
        "pandas",
        "numpy",
        "yaml",
        "tkinter",
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
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(current_dir / "assets" / "icon.ico"),
)
