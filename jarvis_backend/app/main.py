import asyncio
import socket
from os import path
from typing import List, Optional

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from uvicorn import Config

from fastapi_main import fastapi_app
from jarvis_backend.app.schedule.scheduler import create_scheduler, configur_scheduler
from jarvis_backend.sessions.dependencies import db_context_depend, init_defaults


class Server(uvicorn.Server):
    def __init__(self, scheduler: BackgroundScheduler, config: Config):
        super().__init__(config)
        self.scheduler = scheduler

    async def serve(self, sockets: Optional[List[socket.socket]] = None) -> None:
        self.scheduler.start()
        await super().serve()

    def handle_exit(self, sig: int, frame) -> None:
        self.scheduler.shutdown(wait=False)
        return super().handle_exit(sig, frame)


async def main():
    db_context = db_context_depend()
    with db_context.session() as session, session.begin():
        init_defaults(session)
    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.ini')
    scheduler = create_scheduler()
    configur_scheduler(scheduler)
    server = Server(scheduler,
                    config=uvicorn.Config(app=fastapi_app, port=8090, log_config=log_file_path, loop="asyncio"))
    api = asyncio.create_task(server.serve())
    await asyncio.wait([api])


if __name__ == "__main__":
    asyncio.run(main())
