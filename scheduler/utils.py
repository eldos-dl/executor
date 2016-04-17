

class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


def select_slave_node():
    from scheduler.models import Node
    nodes = Node.objects.filter(state='HF')
    if nodes:
        running_jobs = [(node.schedule_set.filter(status='S').count(), - node.status_set.all()[0].memory_available,
                        node.status_set.all()[0].cpu_used_percent) for node in nodes]
        best = min(running_jobs)
        return nodes[running_jobs.index(best)]
    else:
        return Node.objects.get(host=True)


def reschedule_jobs(node):
    import requests
    from ui.models import Schedule
    from ui.serializers import ExecutionRequestSerializer
    from ui.types import ExecutionRequestType
    running_job_list = Schedule.objects.filter(node=node, status='S')
    for job in running_job_list:
        node = select_slave_node()
        job.node = node
        files = [(job.executable.name.split('/')[-1], job.executable.file.file),
                 (job.input_file.name.split('/')[-1], job.input_file.file.file)]
        url = "http://%s:%d/execute/" % (node.ip, node.port)
        print files
        execution_request_serializer = ExecutionRequestSerializer(
            ExecutionRequestType(schedule_id=job.id, time_limit=job.time_limit,
                                 memory_limit=job.memory_limit))
        r = requests.post(url, files=files, data=execution_request_serializer.data)
        if r.status_code == 202:
            # print "job delivered"
            job.status = 'S'
            job.save()
        else:
            job.status = 'F'
            job.save()
            print "error" + str(r.status_code)


def health_check(node, host=None):
    import requests
    from .serializers import StatusSerializer, NodeSerializer
    from .models import Node
    if host is None:
        host_node = Node.objects.get(host=True)
    response = requests.get(node.get_http_endpoint() + "stats/")
    if response.status_code == 200:
        response_serializer = StatusSerializer(data=response.json())
        if response_serializer.is_valid():
            stats = response_serializer.save()
            if stats.leader is None or stats.leader != host_node:
                reschedule_jobs(node)
                host_setializer = NodeSerializer(host_node)
                response = requests.post(node.get_http_endpoint() + "follow/me/", data=host_setializer.data)
        else:
            node.state = 'FF'
            node.save()
            reschedule_jobs(node)
    else:
        node.state = 'FF'
        node.save()
        reschedule_jobs(node)

