import asyncio
import os
import socket
from typing import List, Optional

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from jarvis_backend.app.config.launch import LaunchConfigHolder
from jarvis_backend.app.constants import LOG_CONFIGS, LAUNCH_CONFIGS, WORKER_TO_STATUS
from jarvis_backend.app.fastapi_main import fastapi_app
from jarvis_backend.app.schedule.scheduler import create_scheduler
from jarvis_backend.sessions.dependencies import db_context_depend, init_defaults
from jarvis_backend.support.utils import get_environment_var


class Server(uvicorn.Server):
    def __init__(self, scheduler: AsyncIOScheduler, launch_config_path: str):
        self.config_holder = LaunchConfigHolder(launch_config_path)
        config = uvicorn.Config(
            app=fastapi_app,
            port=self.config_holder.port,
            host="0.0.0.0",
            log_config=LOG_CONFIGS,
            loop="asyncio",
            ssl_keyfile=get_environment_var("CERTIFICATE_KEY_PATH"),
            ssl_certfile=get_environment_var("CERTIFICATE_PATH"),
        )
        super().__init__(config)
        self.scheduler = scheduler

    async def serve(self, sockets: Optional[List[socket.socket]] = None) -> None:
        if self.config_holder.background_enabled:
            self.scheduler.start()
        await super().serve()

    @staticmethod
    def kill_all_workers():
        for identifier in WORKER_TO_STATUS:
            WORKER_TO_STATUS[identifier] = False

    def handle_exit(self, sig: int, frame) -> None:
        if self.config_holder.background_enabled:
            self.kill_all_workers()
            self.scheduler.shutdown(wait=False)
        return super().handle_exit(sig, frame)


async def main():
    db_context = db_context_depend()
    if not os.path.exists("logs"):
        os.mkdir("logs")
    with db_context.session() as session, session.begin():
        init_defaults(session)
    scheduler = create_scheduler()
    server = Server(scheduler, LAUNCH_CONFIGS)
    api = asyncio.create_task(server.serve())
    await asyncio.wait([api])


if __name__ == "__main__":
    asyncio.run(main())
