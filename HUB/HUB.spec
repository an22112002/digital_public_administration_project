# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import (
    collect_all,
    collect_dynamic_libs,
    collect_data_files,
    collect_submodules,
    copy_metadata,
)


# ============================================================
# 1. pyzbar
# ============================================================

pyzbar_binaries = collect_dynamic_libs("pyzbar")


# ============================================================
# 2. PaddlePaddle
# ============================================================

paddle_datas, paddle_binaries, paddle_hiddenimports = collect_all(
    "paddle"
)


# ============================================================
# 3. PaddleX
# ============================================================

paddlex_datas, paddlex_binaries, paddlex_hiddenimports = collect_all(
    "paddlex"
)


# ============================================================
# 4. PaddleOCR
# ============================================================

paddleocr_datas, paddleocr_binaries, paddleocr_hiddenimports = collect_all(
    "paddleocr"
)


# ============================================================
# 5. pypdfium2
# ============================================================

pypdfium2_datas, pypdfium2_binaries, pypdfium2_hiddenimports = collect_all(
    "pypdfium2"
)


# ============================================================
# 6. OpenCV
# ============================================================

opencv_datas, opencv_binaries, opencv_hiddenimports = collect_all(
    "cv2"
)


# ============================================================
# 7. pyclipper
# ============================================================

pyclipper_datas, pyclipper_binaries, pyclipper_hiddenimports = collect_all(
    "pyclipper"
)


# ============================================================
# 8. Other PaddleX / PaddleOCR dependencies
# ============================================================

extra_packages = [
    "shapely",
    "scikit-image",
    "sklearn",
    "scipy",
    "lmdb",
    "rapidfuzz",
    "albumentations",
    "albucore",
    "Pillow",
    "lxml",
    "tokenizers",
    "einops",
    "jinja2",
    "regex",
    "tiktoken",
    "premailer",
    "openpyxl",
    "ftfy",
    "imagesize",
]


# ============================================================
# 9. Collect extra packages
# ============================================================

extra_datas = []
extra_binaries = []
extra_hiddenimports = []

for package in extra_packages:
    try:
        d, b, h = collect_all(package)

        extra_datas += d
        extra_binaries += b
        extra_hiddenimports += h

    except Exception as e:
        print(
            f"[SPEC] Warning: cannot collect package "
            f"{package}: {e}"
        )


# ============================================================
# 10. Distribution metadata
#
# PaddleX sử dụng importlib.metadata / package metadata
# để kiểm tra dependency ở runtime.
# ============================================================

metadata_packages = [
    "paddlepaddle",
    "paddlex",
    "paddleocr",

    "pypdfium2",
    "opencv-contrib-python",
    "pyclipper",

    "shapely",
    "scikit-image",
    "scikit-learn",
    "scipy",

    "lmdb",
    "rapidfuzz",

    "albumentations",
    "albucore",

    "Pillow",
    "lxml",

    "tokenizers",
    "einops",
    "jinja2",
    "regex",
    "tiktoken",

    "premailer",
    "openpyxl",
    "ftfy",
    "imagesize",
]


metadata_datas = []

for package in metadata_packages:
    try:
        metadata_datas += copy_metadata(package)

    except Exception as e:
        print(
            f"[SPEC] Warning: cannot copy metadata "
            f"for {package}: {e}"
        )


# ============================================================
# 11. Merge binaries
# ============================================================

all_binaries = (
    pyzbar_binaries

    + paddle_binaries
    + paddlex_binaries
    + paddleocr_binaries

    + pypdfium2_binaries
    + opencv_binaries
    + pyclipper_binaries

    + extra_binaries
)


# ============================================================
# 12. Merge datas
# ============================================================

all_datas = (
    paddle_datas
    + paddlex_datas
    + paddleocr_datas

    + pypdfium2_datas
    + opencv_datas
    + pyclipper_datas

    + extra_datas

    + metadata_datas

    + [
        # ----------------------------------------------------
        # Application icon
        # ----------------------------------------------------
        ("launcher/icon.ico", "."),

        # ----------------------------------------------------
        # WebView plugin
        # ----------------------------------------------------
        ("plugin/WebView", "plugin/WebView"),

        # ----------------------------------------------------
        # OCR models + OCR code/data
        # ----------------------------------------------------
        ("OCR", "OCR"),
    ]
)


# ============================================================
# 13. Merge hidden imports
# ============================================================

all_hiddenimports = (
    paddle_hiddenimports
    + paddlex_hiddenimports
    + paddleocr_hiddenimports

    + pypdfium2_hiddenimports
    + opencv_hiddenimports
    + pyclipper_hiddenimports

    + extra_hiddenimports
)


# ============================================================
# 14. Explicit imports
#
# Một số dependency được PaddleX import động.
# ============================================================

all_hiddenimports += [
    "pypdfium2",
    "pypdfium2.raw",

    "cv2",
    "pyclipper",

    "shapely",
    "sklearn",
    "skimage",

    "scipy",
    "scipy.ndimage",

    "lmdb",
    "rapidfuzz",

    "albumentations",
    "albucore",

    "tokenizers",
    "einops",

    "jinja2",
    "regex",

    "lxml",

    "paddle",
    "paddleocr",
    "paddlex",
]


# ============================================================
# 15. Analysis
# ============================================================

a = Analysis(
    ["launcher/main.py"],

    pathex=[
        ".",
    ],

    binaries=all_binaries,

    datas=all_datas,

    hiddenimports=all_hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[],

    noarchive=False,

    optimize=0,
)


# ============================================================
# 16. PYZ
# ============================================================

pyz = PYZ(
    a.pure
)


# ============================================================
# 17. EXE
# ============================================================

exe = EXE(
    pyz,

    a.scripts,

    [],

    exclude_binaries=True,

    name="HUB",

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

    icon="launcher/icon.ico",
)


# ============================================================
# 18. COLLECT
# ============================================================

coll = COLLECT(
    exe,

    a.binaries,

    a.datas,

    strip=False,

    upx=True,

    upx_exclude=[],

    name="HUB",
)