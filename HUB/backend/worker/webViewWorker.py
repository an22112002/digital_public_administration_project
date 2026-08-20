from redis.asyncio import Redis
import json, asyncio
from plugin.WebView.main import process_with_webview, DataProcess

from backend.config import REDIS_HOST, REDIS_PASSWORD, REDIS_PORT

redis_client = Redis(host=REDIS_HOST, password=REDIS_PASSWORD, port=REDIS_PORT, db=0, decode_responses=True)

import asyncio
import json
import multiprocessing

class WebViewWorker:

    def __init__(self):
        self.running = False
        self.webview_process = None

    async def run(self):

        self.running = True

        print("[WEBVIEW WORKER] WebView started")

        try:

            while self.running:

                message = await redis_client.blpop(
                    "webview",
                    timeout=1
                )

                if not message:
                    continue

                _, raw_data = message

                data = json.loads(raw_data)

                if not data.get("start"):
                    continue

                webview_data = data["data"]

                url = webview_data["url"]

                data_process = [
                    DataProcess.from_dict(item)
                    for item in webview_data["data_process"]
                ]

                print("[WEBVIEW WORKER] Starting WebView")

                self.webview_process = multiprocessing.Process(
                    target=process_with_webview,
                    args=(
                        url,
                        data_process
                    )
                )

                self.webview_process.start()
                print(
                    f"[WEBVIEW WORKER] "
                    f"WebView PID = {self.webview_process.pid}"
                )

                # Chờ WebView đóng
                await asyncio.to_thread(
                    self.webview_process.join
                )

                await asyncio.sleep(3)
                print(
                    f"[WEBVIEW WORKER] "
                    f"WebView PID {self.webview_process.pid} "
                    f"exitcode = {self.webview_process.exitcode}"
                )

                self.webview_process = None

                print("[WEBVIEW WORKER] WebView closed")

        except asyncio.CancelledError:

            print("[WEBVIEW WORKER] Cancelled")

            raise

        finally:
            self.running = False

            if self.webview_process is not None:

                if self.webview_process.is_alive():

                    self.webview_process.terminate()

                    await asyncio.to_thread(
                        self.webview_process.join
                    )

                self.webview_process = None

    print("[WEBVIEW WORKER] stopped")

    async def stop(self):

        print("[WEBVIEW WORKER] stopping")

        self.running = False

        if self.webview_process is not None:

            if self.webview_process.is_alive():

                print(
                    "[WEBVIEW WORKER] "
                    "Terminating WebView process"
                )

                self.webview_process.terminate()

                await asyncio.to_thread(
                    self.webview_process.join
                )

            self.webview_process = None