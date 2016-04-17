from __future__ import unicode_literals

from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    name = 'scheduler'

    def ready(self):
        import scheduler.signals
        from scheduler.models import Node
        try:
            Node.objects.all().delete()
        except:
            pass
