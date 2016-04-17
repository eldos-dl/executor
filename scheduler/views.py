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
        else:
            return Response(node_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        leader = Node.objects.get(state='HL')
    except:
        leader = None
    response_serializer = StatusSerializer(StatusType(node=host, leader=leader))
    return Response(response_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def follow_me(request):
    import requests
    from .serializers import NodeSerializer
    from .models import Node
    leader_serializer = NodeSerializer(data=request.data)
    if leader_serializer.is_valid():
        leader = leader_serializer.save()
        print leader.get_http_endpoint()
        try:
            follower = Node.objects.get(host=True)
            follower_serializer = NodeSerializer(follower)
            # print "Requesting %s/follower/confirm/" % leader.get_http_endpoint()
            response = requests.post(leader.get_http_endpoint() + "follower/confirm/",
                                     follower_serializer.data)
            if response.status_code == 202:
                follower.state = 'HF'
                follower.save()
                leader.state = 'HL'
                leader.save()
                print "Following Node " + leader.get_http_endpoint()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(leader_serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(leader_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def confirm_follower(request):
    from .serializers import NodeSerializer
    follower_serializer = NodeSerializer(data=request.data)
    if follower_serializer.is_valid():
        follower_node = follower_serializer.save()
        if follower_node.state in ['RF', 'FF']:
            follower_node.state = 'HF'
            follower_node.save()
            print "Leading Node " + follower_node.get_http_endpoint()
            return Response({'msg': 'CONFIRMED'}, status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'msg': 'DENIED'}, status=status.HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response(follower_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def execute(request):
    from .serializers import ExecutionSerializer
    files = list(request.FILES.values())
    payload = request.data
    # payload[]
    # payload['time_limit'] = request.data['time_limit']
    # payload['memory_limit'] = request.data['memory_limit']
    payload['executable_file'] = files[0]
    if len(files) > 1:
        payload['input_file'] = files[0]
        payload['executable_file'] = files[1]
    print payload
    print files
    execute_serializer = ExecutionSerializer(data=payload)
    print execute_serializer.is_valid()
    if execute_serializer.is_valid():
        execute_serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    print execute_serializer.errors
    return Response(data=execute_serializer.errors, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['POST'])
def update_output(request):
    from .serializers import ExecutionResponseSerializer
    from ui.models import UserFiles
    files = list(request.FILES.values())
    request_serializer = ExecutionResponseSerializer(data=request.data)
    print request_serializer.is_valid()
    print request_serializer.validated_data
    if request_serializer.is_valid():
        schedule = request_serializer.save()
        print schedule.status
        UserFiles.objects.create(file=files[0], user=schedule.user, name=files[0].name, type='O')
        return Response(status=status.HTTP_202_ACCEPTED)
    return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(['POST'])
def lead_nodes(request):
    from .serializers import NodeSerializer, StatusSerializer
    from .models import Node
    import requests
    request_serializer = NodeSerializer(data=request.data, many=True)
    if request_serializer.is_valid():
        nodes = request_serializer.save()
        host_node = Node.objects.get(host=True)
        host_node.state = 'C'
        host_node.save()
        host_setializer = NodeSerializer(host_node)
        # print nodes
        for node in nodes:
            # try:
            node.state = 'RF'
            node.save()
            # print node
            # print "Requesting %s/stats/" % node.get_http_endpoint()
            response = requests.post(node.get_http_endpoint() + "stats/", data=host_setializer.data)
            stats_serializer = StatusSerializer(data=response.json())
            if stats_serializer.is_valid():
                stats = stats_serializer.save()
            else:
                return Response(data=stats_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # print "Requesting %s/follow/me/" % node.get_http_endpoint()
            response = requests.post(node.get_http_endpoint() + "follow/me/", data=host_setializer.data)
            if response.status_code != 200:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            # except:
            #     return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_200_OK)
