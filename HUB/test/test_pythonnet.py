import sys
from pathlib import Path

import clr_loader

print("=== Python ===")
print(sys.executable)
print(sys.maxsize)

print("=== clr_loader ===")
import clr_loader.ffi as ffi_module
print(ffi_module.__file__)

print("=== ClrLoader ===")
dirname = Path(ffi_module.__file__).parent / "dlls"
path = dirname / ("amd64" if sys.maxsize > 2**32 else "x86") / "ClrLoader.dll"
print(path)
print("exists:", path.exists())

print("=== load_netfx ===")
rt = clr_loader.get_netfx()
print(rt.info())

print("=== pythonnet ===")
import clr
from System import String

print(String("PYTHONNET OK"))

import os

print("=== ENV ===")
print("PATH:")
print(os.environ.get("PATH"))

print("=== BASE ===")
print("__file__:", __file__)
print("cwd:", os.getcwd())

import sys
print("sys._MEIPASS:", getattr(sys, "_MEIPASS", None))