from apscheduler.triggers.interval import IntervalTrigger

from jarvis_backend.app.config.background import BackgroundConfigHolder
from jarvis_backend.app.constants import BACKGROUND_CONFIGS, WORKER_TO_STATUS
from jarvis_backend.app.schedule.simple_task import SimpleTask
from jarvis_backend.app.schedule.workers.cache import CacheWorker
from jarvis_backend.app.schedule.workers.load import LoadWorker
from jarvis_backend.app.schedule.workers.update import UpdateWorker
from jarvis_backend.sessions.dependencies import db_context_depend


def __cache_update():
    db_context = db_context_depend()
    cache_worker = CacheWorker(db_context)
    WORKER_TO_STATUS[CacheWorker.get_identifier()] = True
    cache_worker.update_all_caches()


def __load_niches(load_skip: int):
    db_context = db_context_depend()
    load_worker = LoadWorker(db_context, load_skip)
    WORKER_TO_STATUS[LoadWorker.get_identifier()] = True
    load_worker.load_niches()


def __update_niches():
    db_context = db_context_depend()
    load_worker = UpdateWorker(db_context)
    WORKER_TO_STATUS[UpdateWorker.get_identifier()] = True
    load_worker.update_niches()


background_config = BackgroundConfigHolder(BACKGROUND_CONFIGS)
SIMPLE_TASKS = []

if background_config.cache_enabled:
    SIMPLE_TASKS.append(SimpleTask(__cache_update, IntervalTrigger(days=1), identifier=CacheWorker.get_identifier()))

if background_config.load_enabled:
    SIMPLE_TASKS.append(SimpleTask(__load_niches, IntervalTrigger(days=7),
                                   identifier=LoadWorker.get_identifier(), args=[background_config.load_skip]))

if background_config.update_enabled:
    SIMPLE_TASKS.append(SimpleTask(__update_niches, IntervalTrigger(days=1), identifier=UpdateWorker.get_identifier()))
