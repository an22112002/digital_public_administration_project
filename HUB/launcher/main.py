import os
import threading

import uvicorn

from backend.main import Backend
from launcher.startup import StartupGuard
from launcher.tray import TrayApp


def run_backend(backend: Backend, server: uvicorn.Server, tray: TrayApp):

    print("[BACKEND] Starting Uvicorn...")
    try:

        server.run()
    except SystemExit:
        print("[MAIN] Exiting all")
        os._exit(0)        
    finally:
        tray.set_status(TrayApp.STATUS_CLOSING)

    print("[BACKEND] Uvicorn stopped")


def main():
    startup_guard = StartupGuard()

    if not startup_guard.acquire():
        return

    try:

        # ==============================
        # Backend
        # ==============================

        backend = Backend(
            host="0.0.0.0",
            port=8000,
        )

        config = uvicorn.Config(
            backend.app,
            host=backend.host,
            port=backend.port,
            log_level="info",
            timeout_graceful_shutdown=5,
        )

        server = uvicorn.Server(config)

        tray = TrayApp(server)
        backend.on_started = tray.set_running_status

        # ==============================
        # Backend thread
        # ==============================

        backend_thread = threading.Thread(
            target=run_backend,
            args=(backend, server, tray),
            daemon=True,
        )

        backend_thread.start()

        # ==============================
        # Tray
        # ==============================

        tray.run()

        # ==============================
        # Wait backend
        # ==============================

        backend_thread.join()

    except SystemExit:
        print("[MAIN] Exiting...")
        exit(0)
    finally:
        if "tray" in locals():
            tray.set_status(TrayApp.STATUS_CLOSING)
        startup_guard.release()

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()

    main()