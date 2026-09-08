from redis.asyncio import Redis
import json, asyncio
from plugin.WebView.main import process_with_webview, DataProcess

import asyncio
import json
import traceback
from backend.log.main import log_exception

class WebViewWorker:

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.running = False

    async def run(self):

        self.running = True

        await self.redis_client.hset(
            "worker:webview",
            "running",
            "1"
        )

        print(
            "[WEBVIEW WORKER] Started"
        )

        try:

            while True:

                # ========================================
                # CHECK ALLOW
                # ========================================

                allow = await self.redis_client.hget(
                    "worker:webview",
                    "allow"
                )

                if str(allow) != "1":

                    print(
                        "[WEBVIEW WORKER] "
                        "allow=False, stopping..."
                    )

                    break

                # ========================================
                # REDIS JOB
                # ========================================

                message = await self.redis_client.blpop(
                    "webview",
                    timeout=1
                )

                if not message:
                    continue

                _, raw_data = message

                data = json.loads(
                    raw_data
                )

                if not data.get("start"):
                    continue

                webview_data = data["data"]

                url = webview_data["url"]

                data_process = [
                    DataProcess.from_dict(item)
                    for item in webview_data[
                        "data_process"
                    ]
                ]

                print(
                    "[WEBVIEW WORKER] "
                    "Starting WebView"
                )

                # ========================================
                # CHẠY WEBVIEW TRỰC TIẾP
                # Process hiện tại chính là WebView process
                # ========================================

                process_with_webview(
                    url,
                    data_process
                )

                print(
                    "[WEBVIEW WORKER] "
                    "WebView closed"
                )

        except asyncio.CancelledError:

            print(
                "[WEBVIEW WORKER] Cancelled"
            )

            raise

        except Exception as e:

            log_exception(e, "worker")
            traceback.print_exc()

        finally:

            self.running = False

            await self.redis_client.hset(
                "worker:webview",
                "running",
                "0"
            )

            print(
                "[WEBVIEW WORKER] Stopped"
            )