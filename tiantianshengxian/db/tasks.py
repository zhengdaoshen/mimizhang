import os
import django

from celery import Celery
from django.core.mail import send_mail

app = Celery('db.tasks', broker='redis://192.168.12.197:6379/3')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiantianshengxian.settings")
django.setup()


@app.task
def task_send_mail(subject, message, sender, receiver, html_message):
    send_mail(subject, message, sender, receiver, html_message=html_message)  # 发送
