from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

job_stores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
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
    scheduler.configure(jobstores=job_stores, executors=executors, job_defaults=job_defaults, timezone=utc)
    return scheduler


def configur_scheduler(scheduler: BackgroundScheduler) -> None:
    # scheduler.add_job(task, IntervalTrigger(seconds=5), id='halo_task')
    pass
