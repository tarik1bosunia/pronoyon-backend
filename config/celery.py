import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery('replycompass')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Optional: Configure periodic tasks
app.conf.beat_schedule = {
    # Example task - runs every 30 minutes
    # 'cleanup-expired-sessions': {
    #     'task': 'apps.core.tasks.cleanup_expired_sessions',
    #     'schedule': crontab(minute='*/30'),
    # },
}

# Optional: Set task result expiration
app.conf.result_expires = 3600  # 1 hour
