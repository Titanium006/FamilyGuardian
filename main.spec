# -*- mode: python ; coding: utf-8 -*-

added_files = [
    ('D:/大三下/软工课设/HomeSurface/utils', 'utils'),  # 将 utils 文件夹打包到名为 'utils' 的目录下
    ('D:/大三下/软工课设/HomeSurface/LAV Filters', 'LAV Filters'),
    ('D:/大三下/软工课设/HomeSurface/myDesign_win','myDesign_win')
]

a = Analysis(
    ['main.py'],
    pathex=["D:/大三下/软工课设/HomeSurface","D:/大三下/软工课设/HomeSurface/LAV Filters","D:/大三下/软工课设/HomeSurface/utils","D:/大三下/软工课设/HomeSurface/myDesign_win"],
    binaries=[("D:/大三下/软工课设/HomeSurface/pt/best.pt","pt")],
    datas=added_files,
    hiddenimports=['Crypto','pycryptodome','pycrypto'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='homesafe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='homesafe',
)
