from __future__ import absolute_import, unicode_literals
from celery import shared_task
from db import stats
from db import run
from db import create_steps, create_step 

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task(name='celery_tasks.update_stats')
def update_stats(action, student):
    logger.info("update_stats({},{})".format(action, student))
    return stats(action,student)

@shared_task(name='celery_tasks.run_steps')
def launch_steps():
    logger.info("run_steps()")
    return run_steps()

@shared_task(name='celery_tasks.run_stats')
def launch_stats():
    logger.info("run_stats('create')")
    return run_stats(None, None)

@shared_task(name='celery_tasks.run')
def launch_run(arguments):
    logger.info("run({})".format(arguments))
    return run(arguments)
