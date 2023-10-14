from apscheduler.triggers.interval import IntervalTrigger

from jarvis_backend.app.config.background import BackgroundConfigHolder
from jarvis_backend.app.constants import BACKGROUND_CONFIGS
from jarvis_backend.app.schedule.simple_task import SimpleTask
from jarvis_backend.app.schedule.workers.cache import CacheWorker
from jarvis_backend.sessions.dependencies import db_context_depend


def __cache_update():
    db_context = db_context_depend()
    cache_worker = CacheWorker(db_context)
    cache_worker.update_all_caches()


background_config = BackgroundConfigHolder(BACKGROUND_CONFIGS)

SIMPLE_TASKS = []

if background_config.cache_enabled:
    SIMPLE_TASKS.append(SimpleTask(__cache_update, IntervalTrigger(days=1), identifier='calc_cache'))
