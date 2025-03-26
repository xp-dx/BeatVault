# from celery import Celery
# from sms.service import send_sms_code

# celery_app = Celery("worker", broker="redis://localhost:6379/0")


# @celery_app.task
# def send_sms_async(phone: str):
#     send_sms_code(phone)
