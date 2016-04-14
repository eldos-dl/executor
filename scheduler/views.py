from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# TODO: Handle Hostname Case
@api_view(['GET', 'POST'])
def get_stats(request):
    from .serializers import StatusSerializer, NodeSerializer
    from .types import StatusType
    from .models import Node
    try:
        host = Node.objects.get(host=True)
    except:
        if ':' in request.META['HTTP_HOST']:
            ip, port = request.META['HTTP_HOST'].split(':')
        else:
            ip, port = request.META['HTTP_HOST'], 80
        node_serializer = NodeSerializer(data={'ip': ip, 'port': port, 'host': True})
        if node_serializer.is_valid():
            host = node_serializer.save()
    response_serializer = StatusSerializer(StatusType(node=host))
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def follow_me(request):
    import requests
    from .serializers import NodeSerializer
    from .models import Node
    leader_serializer = NodeSerializer(data=request.data)
    if leader_serializer.is_valid():
        follower = leader_serializer.save()
        try:
            follower_serializer = NodeSerializer(Node.objects.get(host=True))
            if follower_serializer.is_valid():
                response = requests.post("http://%s:%d/follower/confirm/" % (follower.ip, follower.port),
                                         follower_serializer.validated_data)
                if response.status_code == 202:
                    follower_serializer.save(state='HF')
                    leader_serializer.save(state='HL')
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(leader_serializer.data)
    else:
        return Response(leader_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def confirm_follower(request):
    from .serializers import NodeSerializer
    follower_serializer = NodeSerializer(data=request.data)
    if follower_serializer.is_valid():
        follower_node = follower_serializer.save()
        if follower_node.state == 'RF':
            follower_node.state = 'HF'
            follower_node.save()
            return Response({'msg': 'CONFIRMED'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'msg': 'DENIED'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response(follower_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
