import asyncio
import logging
from abc import abstractmethod

from jarvis_backend.app.loggers import BACKGROUND_LOGGER

logger = logging.getLogger(BACKGROUND_LOGGER)


class Task:
    def __init__(self, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs


class __BackgroundWorker:
    def __init__(self, task: Task, delay_in_seconds):
        self.task: Task = task
        self.delay_in_seconds = delay_in_seconds
        self.__is_alive = False

    async def start(self):
        self.__is_alive = True
        while self.__is_alive:
            self.task.method(*self.task.args, **self.task.kwargs)
            await asyncio.sleep(self.delay_in_seconds)

    def kill(self):
        logger.info(self.get_message_on_kill())
        self.__is_alive = False

    def get_message_on_kill(self) -> str:
        args_string = ','.join([*self.task.args]) + ','.join([f'{key}={self.task.kwargs[key]}'
                                                              for key in self.task.kwargs])
        return f'Worker with task: {self.task.method.__name__}({args_string}) was killed'


class SimpleWorker(__BackgroundWorker):
    def __init__(self, delay_in_seconds: int):
        super().__init__(Task(self.task), delay_in_seconds)

    @abstractmethod
    def task(self):
        pass

    def get_message_on_kill(self) -> str:
        return f'{self.__class__.__name__} worker was killed'
