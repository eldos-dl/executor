
class ExecutionRequestType(object):
    def __init__(self, **kwargs):
        self.time_limit = kwargs['time_limit']
        self.memory_limit = kwargs['memory_limit']
        self.schedule_id = kwargs['schedule_id']