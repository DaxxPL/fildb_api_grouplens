# django_with_celery/celery.py
from __future__ import absolute_import
import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fimdb_api_grouplens.settings')
app = Celery('fimdb_api_grouplens')
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])
app.autodiscover_tasks()
CELERY_TIMEZONE = 'Europe/London'
app.Task.track_started
