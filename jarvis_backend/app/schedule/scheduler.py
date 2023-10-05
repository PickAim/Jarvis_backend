from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from jarvis_backend.app.schedule.tasks import SIMPLE_TASKS

job_stores = {
    # 'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=10)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 5
}


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    __configure_scheduler(scheduler)
    return scheduler


def __configure_scheduler(scheduler: BackgroundScheduler) -> None:
    scheduler.configure(jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone=utc)
    for task in SIMPLE_TASKS:
        scheduler.add_job(task.function, task.trigger_interval, id=task.identifier)
