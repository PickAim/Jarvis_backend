import asyncio
import socket
from typing import List, Optional

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler

from fastapi_main import fastapi_app
from jarvis_backend.app.config_holder import LaunchConfigHolder
from jarvis_backend.app.constants import LOG_CONFIGS, LAUNCH_CONFIGS
from jarvis_backend.app.schedule.scheduler import create_scheduler
from jarvis_backend.sessions.dependencies import db_context_depend, init_defaults


class Server(uvicorn.Server):
    def __init__(self, scheduler: BackgroundScheduler, launch_config_path: str):
        self.config_holder = LaunchConfigHolder(launch_config_path)
        config = uvicorn.Config(app=fastapi_app, port=self.config_holder.port,
                                log_config=LOG_CONFIGS, loop="asyncio")
        super().__init__(config)
        self.scheduler = scheduler

    async def serve(self, sockets: Optional[List[socket.socket]] = None) -> None:
        if self.config_holder.enabled_background:
            self.scheduler.start()
        await super().serve()

    def handle_exit(self, sig: int, frame) -> None:
        if self.config_holder.enabled_background:
            self.scheduler.shutdown(wait=False)
        return super().handle_exit(sig, frame)


async def main():
    db_context = db_context_depend()
    with db_context.session() as session, session.begin():
        init_defaults(session)
    scheduler = create_scheduler()
    server = Server(scheduler, LAUNCH_CONFIGS)
    api = asyncio.create_task(server.serve())
    await asyncio.wait([api])


if __name__ == "__main__":
    asyncio.run(main())
