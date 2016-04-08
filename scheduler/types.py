__author__ = 'eldos'


class StatsType(object):
    def __init__(self, **kwargs):
        if kwargs:
            self.memory_total = kwargs['memory_total']
            self.memory_available = kwargs['memory_available']
            self.memory_used_percent = kwargs['memory_used_percent']
            self.cpu_count = kwargs['cpu_count']
            self.cpu_used_percent = kwargs['cpu_used_percent']
            self.cpu_idle_percent = kwargs['cpu_idle_percent']
        else:
            import psutil
            memory = psutil.virtual_memory()
            self.memory_available = memory.available
            self.memory_total = memory.total
            self.memory_used_percent = memory.percent
            self.cpu_count = psutil.cpu_count()
            self.cpu_used_percent = psutil.cpu_percent()
            self.cpu_idle_percent = psutil.cpu_times_percent().idle
