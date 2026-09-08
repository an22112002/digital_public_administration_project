# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all


# ============================================================
# 1. pywebview
# ============================================================

webview_datas, webview_binaries, webview_hiddenimports = collect_all(
    "webview"
)


# ============================================================
# 2. pythonnet
# ============================================================

pythonnet_datas, pythonnet_binaries, pythonnet_hiddenimports = collect_all(
    "pythonnet"
)


# ============================================================
# 3. clr_loader
# ============================================================

clr_loader_datas, clr_loader_binaries, clr_loader_hiddenimports = collect_all(
    "clr_loader"
)


# ============================================================
# 4. Merge
# ============================================================

datas = (
    webview_datas
    + pythonnet_datas
    + clr_loader_datas
)

binaries = (
    webview_binaries
    + pythonnet_binaries
    + clr_loader_binaries
)

hiddenimports = (
    webview_hiddenimports
    + pythonnet_hiddenimports
    + clr_loader_hiddenimports

    + [
        "webview",
        "webview.guilib",

        # Windows backend
        "webview.platforms.winforms",

        # Edge Chromium backend
        "webview.platforms.edgechromium",

        # Python.NET
        "pythonnet",
        "clr",

        # clr-loader
        "clr_loader",
        "clr_loader.netfx",
    ]
)


# ============================================================
# 5. Analysis
# ============================================================

a = Analysis(
    ["test_webview.py"],

    pathex=["."],

    binaries=binaries,

    datas=datas,

    hiddenimports=hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,

    optimize=0,
)


# ============================================================
# 6. PYZ
# ============================================================

pyz = PYZ(
    a.pure
)


# ============================================================
# 7. EXE
# ============================================================

exe = EXE(
    pyz,

    a.scripts,

    [],

    exclude_binaries=True,

    name="test_webview",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    # KHÔNG UPX khi debug Python.NET
    upx=False,

    # Giữ console để xem traceback
    console=True,

    disable_windowed_traceback=False,

    argv_emulation=False,

    target_arch=None,

    codesign_identity=None,

    entitlements_file=None,
)


# ============================================================
# 8. COLLECT
# ============================================================

coll = COLLECT(
    exe,

    a.binaries,

    a.datas,

    strip=False,

    # KHÔNG UPX
    upx=False,

    upx_exclude=[],

    name="test_webview",
)