from celery.app import shared_task

from .models import Node
from .serializers import StatusSerializer


@shared_task
def heart_beat():
    import requests
    for node in Node.objects.all():
        response = requests.get(node.get_http_endpoint() + "stats/")
        response_serializer = StatusSerializer(data=response.json())
        if response_serializer.is_valid():
            status = response_serializer.save()
        print status.last_updated
