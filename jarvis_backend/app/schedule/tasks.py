from apscheduler.triggers.interval import IntervalTrigger

from jarvis_backend.app.schedule.simple_task import SimpleTask
from jarvis_backend.app.schedule.workers.cache import CacheWorker
from jarvis_backend.sessions.dependencies import db_context_depend


def __cache_update():
    db_context = db_context_depend()
    cache_worker = CacheWorker(db_context)
    cache_worker.update_all_caches()


SIMPLE_TASKS = [
    SimpleTask(__cache_update, IntervalTrigger(seconds=80), identifier='calc_cache')
]
