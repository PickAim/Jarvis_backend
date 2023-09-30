import asyncio
from os import path

import uvicorn

from fastapi_main import fastapi_app
from jarvis_backend.app.workers.cache_worker import CacheWorker
from jarvis_backend.sessions.dependencies import db_context_depends, init_defaults

worker = CacheWorker()


class Server(uvicorn.Server):
    def handle_exit(self, sig: int, frame) -> None:
        worker.kill()
        return super().handle_exit(sig, frame)


async def main():
    db_context = db_context_depends()
    with db_context.session() as session, session.begin():
        init_defaults(session)
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.ini')

    server = Server(config=uvicorn.Config(app=fastapi_app, port=8090, log_config=log_file_path, loop="asyncio"))
    api = asyncio.create_task(server.serve())
    worker_process = asyncio.create_task(worker.start())
    await asyncio.wait([api, worker_process])


if __name__ == "__main__":
    asyncio.run(main())
