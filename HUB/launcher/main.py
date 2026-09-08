import threading

import uvicorn

from backend.main import Backend
from launcher.tray import TrayApp


def run_backend(backend: Backend, server: uvicorn.Server):

    print("[BACKEND] Starting Uvicorn...")

    server.run()

    print("[BACKEND] Uvicorn stopped")


def main():

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

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()

    main()