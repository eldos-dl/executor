from celery.app import shared_task

from .models import Node


# TODO: Retry Requests
@shared_task
def heart_beat():
    from .utils import health_check
    for node in Node.objects.filter(state__in=['HF', 'FF']):
        health_check(node)
