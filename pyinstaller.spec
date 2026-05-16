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
        (str(src_dir / "cli"), "src/cli"),
        (str(src_dir / "tui"), "src/tui"),
        (str(src_dir / "export"), "src/export"),
        (str(src_dir / "wechat_scanner"), "src/wechat_scanner"),
        (str(src_dir / "wechat_image"), "src/wechat_image"),
        (str(src_dir / "wechat_integration"), "src/wechat_integration"),
        ("README.md", "."),
        ("README_zh.md", "."),
        ("config", "config"),
    ],
    hiddenimports=[
        "flask",
        "flask_cors",
        "bs4",
        "lxml",
        "PIL",
        "pandas",
        "numpy",
        "yaml",
        "tkinter",
        "src.clone",
        "src.debate",
        "src.share",
        "src.web",
        "src.cli",
        "src.tui",
        "src.export",
        "src.wechat_scanner",
        "src.wechat_image",
        "src.wechat_integration",
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
)
