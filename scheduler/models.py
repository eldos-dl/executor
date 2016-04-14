from __future__ import unicode_literals
from datetime import timedelta

from django.db import models

from ui.models import UserFiles


class Node(models.Model):
    NODE_STATES = (('HL', 'Healthy Leader'), ('C', 'Candidate'),
                   ('HS', 'Healthy Single'), ('HF', 'Healthy Follower'),
                   ('FF', 'Failed Follower'), ('FL', 'Failed Leader'),
                   ('RF', 'Requested to Follow'))
    ip = models.GenericIPAddressField(protocol='IPv4', default='127.0.0.1')
    port = models.IntegerField(default=80)
    state = models.CharField(max_length=2, choices=NODE_STATES, default='HS')
    host = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ip', 'port')

    def __repr__(self):
        return "<Node %s: %s:%d>" % (self.state, self.ip, self.port)

    def get_http_endpoint(self):
        return "http://%s:%d/" % (self.ip, self.port)


class Status(models.Model):
    memory_used_percent = models.FloatField(default=0.0)
    memory_available = models.BigIntegerField(default=0)
    memory_total = models.BigIntegerField(default=0)
    cpu_total = models.IntegerField(default=1)
    cpu_used_percent = models.FloatField(default=0.0)
    cpu_idle_percent = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    node = models.ForeignKey(to=Node, null=True, blank=True)


class Schedule(models.Model):
    node = models.ForeignKey(to=Node)
    executable = models.ForeignKey(to=UserFiles, related_name='executables')
    input_file = models.ForeignKey(to=UserFiles, blank=True, null=True, related_name='input_files')
    output_file = models.ForeignKey(to=UserFiles, blank=True, null=True, related_name='output_files')
    time_limit = models.DurationField(default=timedelta(30))
    memory_limit = models.BigIntegerField(default=134217728)


def exec_directory_path(instance, filename):
    return 'exec/.{1}'.format(filename)


class Execution(models.Model):
    executable_file = models.FileField(upload_to=exec_directory_path)
    input_file = models.FileField(upload_to=exec_directory_path)
    output_file = models.FileField(upload_to=exec_directory_path)
    time_limit = models.DurationField(default=timedelta(30))
    memory_limit = models.BigIntegerField(default=134217728)
    time_taken = models.DurationField(blank=True, null=True)
    memory_used = models.BigIntegerField(blank=True, null=True)
