from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from ..core.exceptions import SchedulerError
import logging

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}

    def start(self):
        try:
            self.scheduler.start()
            logger.info("Scheduler started")
        except Exception as e:
            raise SchedulerError(f"Error starting scheduler: {str(e)}")

    def add_job(self, job_id: str, func, trigger, **trigger_args):
        try:
            job = self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                **trigger_args
            )
            self.jobs[job_id] = job
            logger.info(f"Added job {job_id}")
            return job
        except Exception as e:
            raise SchedulerError(f"Error adding job: {str(e)}")

    def remove_job(self, job_id: str):
        try:
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                logger.info(f"Removed job {job_id}")
        except Exception as e:
            raise SchedulerError(f"Error removing job: {str(e)}")

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

    def get_all_jobs(self):
        return self.jobs

# Створення глобального екземпляру планувальника
scheduler = Scheduler() 