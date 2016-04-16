from celery.app import shared_task

from .models import Node
from .serializers import StatusSerializer


# TODO: Retry Requests
@shared_task
def heart_beat():
    import requests
    from .utils import reschedule_jobs
    for node in Node.objects.filter(state__in=['HF', 'FF']):
        response = requests.get(node.get_http_endpoint() + "stats/")
        if response.status_code == 200:
            response_serializer = StatusSerializer(data=response.json())
            if response_serializer.is_valid():
                response_serializer.save()
            else:
                node.state = 'FF'
                node.save()
                reschedule_jobs(node)
        else:
            node.state = 'FF'
            node.save()
            reschedule_jobs(node)
