from __future__ import absolute_import
from datetime import timedelta

import os

from celery.schedules import crontab
import celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'executor.settings')
app = celery.Celery('executor')
app.conf.update(
    BROKER_URL='django://',
    CELERY_TIMEZONE='UTC',
    CELERYBEAT_SCHEDULE={
        'heartbeat': {
            'task': 'scheduler.tasks.heart_beat',
            'schedule': timedelta(seconds=30)
        }
    },
    CELERY_IMPORTS=('scheduler.tasks',)
)
