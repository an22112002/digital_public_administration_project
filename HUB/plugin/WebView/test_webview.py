import sys
import traceback


print("=" * 70)
print("WEBVIEW / PYTHONNET DIAGNOSTIC")
print("=" * 70)

print("Python:", sys.version)
print("Frozen:", getattr(sys, "frozen", False))
print("Executable:", sys.executable)

try:
    print("\n[1] Import webview")
    import webview
    print("    OK")
    print("    Version:", getattr(webview, "__version__", "unknown"))

except Exception:
    print("    FAILED")
    traceback.print_exc()
    input("\nPress ENTER to exit...")
    raise


try:
    print("\n[2] Import pythonnet")
    import pythonnet
    print("    OK")
    print("    Path:", pythonnet.__file__)

except Exception:
    print("    FAILED")
    traceback.print_exc()
    input("\nPress ENTER to exit...")
    raise


try:
    print("\n[3] Import clr")
    import clr
    print("    OK")
    print("    Path:", clr.__file__)

except Exception:
    print("    FAILED")
    traceback.print_exc()
    input("\nPress ENTER to exit...")
    raise


try:
    print("\n[4] Import clr_loader")
    import clr_loader
    print("    OK")
    print("    Path:", clr_loader.__file__)

except Exception:
    print("    FAILED")
    traceback.print_exc()
    input("\nPress ENTER to exit...")
    raise


try:
    print("\n[5] Import clr_loader.netfx")
    import clr_loader.netfx
    print("    OK")

except Exception:
    print("    FAILED")
    traceback.print_exc()
    input("\nPress ENTER to exit...")
    raise


try:
    print("\n[6] Import WinForms backend")
    from webview.platforms import winforms
    print("    OK")
    print("    Module:", winforms.__file__)

except Exception:
    print("    FAILED")
    traceback.print_exc()
    input("\nPress ENTER to exit...")
    raise


try:
    print("\n[7] Create WebView window")
    webview.create_window(
        "HUB WebView Test",
        "https://www.google.com",
        width=1000,
        height=700,
    )

    print("    Window created")

except Exception:
    print("    FAILED")
    traceback.print_exc()
    input("\nPress ENTER to exit...")
    raise


try:
    print("\n[8] Start WebView")
    print("    Starting...")

    webview.start()

    print("    WebView exited normally")

except Exception:
    print("    FAILED")
    traceback.print_exc()


print("\n" + "=" * 70)
print("TEST FINISHED")
print("=" * 70)

input("Press ENTER to exit...")