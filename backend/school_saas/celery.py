import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_saas.settings')

app = Celery('school_saas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
