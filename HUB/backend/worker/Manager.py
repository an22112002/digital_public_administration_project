import asyncio
from backend.worker.webViewWorker import WebViewWorker

class WorkerManager:

    def __init__(self):
        self.workers = [
            WebViewWorker()
        ]
        self.tasks = []

    async def start(self):

        for worker in self.workers:

            task = asyncio.create_task(
                worker.run()
            )

            self.tasks.append(task)
            
        print("All workers started")

    async def stop(self):

        print("Stopping workers...")

        for worker in self.workers:
            await worker.stop()

        await asyncio.gather(
            *self.tasks,
            return_exceptions=True
        )

        print("All workers stopped")