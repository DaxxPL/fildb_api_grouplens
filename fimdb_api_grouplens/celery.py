# django_with_celery/celery.py
from __future__ import absolute_import
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fimdb_api_grouplens.settings')
app = Celery('fimdb_api_grouplens')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
