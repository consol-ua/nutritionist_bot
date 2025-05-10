from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
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
            logger.info("Планувальник завдань запущено")
        except Exception as e:
            raise SchedulerError(f"Помилка запуску планувальника: {str(e)}")

    def add_job(self, job_id: str, func, trigger: str, **trigger_args):
        try:
            job = self.scheduler.add_job(
                func,
                trigger=CronTrigger.from_crontab(trigger),
                id=job_id,
                **trigger_args
            )
            self.jobs[job_id] = job
            logger.info(f"Додано завдання {job_id}")
            return job
        except Exception as e:
            raise SchedulerError(f"Помилка додавання завдання: {str(e)}")

    def remove_job(self, job_id: str):
        try:
            if job_id in self.jobs:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                logger.info(f"Видалено завдання {job_id}")
        except Exception as e:
            raise SchedulerError(f"Помилка видалення завдання: {str(e)}")

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

    def get_all_jobs(self):
        return self.jobs

# Створення глобального екземпляру планувальника
scheduler = Scheduler() 