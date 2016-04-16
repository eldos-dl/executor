def getNode():
    #pass
    from scheduler.models import Status
    from scheduler.models import Node
    nodes = Node.objects.filter(state='HF');
    from ui.models import Schedule
    for node in nodes:
        running_job_list = Schedule.objects.filter(node=node, status='S')
        node['num_of_jobs'] = len(running_job_list)
    nodelist = sorted(nodes, key=lambda x: x.num_of_jobs, reverse=False)
    min = nodelist[0].num_of_jobs
    count = 0
    for i in nodelist:
        if i.num_of_jobs == min:
            count += 1

    if count > 1:
        minlist = nodelist[0:count]
        for node in minlist:
            statuslist = Status.objects.filter(node=node)
            node['cpu'] = statuslist[0]['cpu_idle_percent']
            node['mem'] = statuslist[0]['memory_available']
        finallist = sorted(minlist, key=lambda x: x.mem, reverse=True)

    else:
        finallist = nodelist

    return finallist[0]



def reschedule(node):
    from .models import Node
    import requests
    from ui.models import Schedule
    from ui.serializers import ExecutionRequestSerializer
    from ui.types import ExecutionRequestType
    running_job_list = Schedule.objects.filter(node=node, status='S')
    for job in running_job_list:
        executable_file = job['executable_file']
        input_file = job['input_file']
        # reschedule them .
        node = getNode()
        # node = Node.objects.get(host=True)
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
