import os
import threading

import uvicorn

from backend.main import Backend
from launcher.tray import TrayApp


def run_backend(backend: Backend, server: uvicorn.Server):

    print("[BACKEND] Starting Uvicorn...")
    try:

        server.run()
    except SystemExit:
        print("[MAIN] Exiting all")
        os._exit(0)        

    print("[BACKEND] Uvicorn stopped")


def main():
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

        # ==============================
        # Backend thread
        # ==============================

        backend_thread = threading.Thread(
            target=run_backend,
            args=(backend, server),
            daemon=True,
        )

        backend_thread.start()

        # ==============================
        # Tray
        # ==============================

        tray = TrayApp(server)

        tray.run()

        # ==============================
        # Wait backend
        # ==============================

        backend_thread.join()
    except SystemExit:
        print("[MAIN] Exiting...")
        exit(0)

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()

    main()