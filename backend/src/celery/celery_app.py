from celery import Celery
from .. import config as _global_config

celery_app = Celery(
    "worker",
    broker=_global_config.CELERY_BROKER_URL,
    backend=_global_config.CELERY_RESULT_BACKEND,
    include=[
        "src.celery.qr.tasks",
        "src.celery.sms.tasks",
        "src.celery.email.tasks",
    ],
)

celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# if __name__ == "__main__":
#     celery_app.start()
