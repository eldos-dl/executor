from __future__ import unicode_literals
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User


def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class UserFiles(models.Model):
    user = models.ForeignKey(to=User)
    file = models.FileField(upload_to=user_directory_path)
    name = models.CharField(max_length=256)
    type = models.CharField(max_length=1, default='E')
    last_updated = models.DateTimeField(auto_now=True)


class Schedule(models.Model):
    from scheduler.models import Node
    SCHEDULE_STATUS = (('S', 'Scheduled'), ('C', 'Completed Successfully'), ('W', 'Waiting to be Scheduled'),
                       ('F', 'Failed to Schedule'), ('E', 'Completed with Errors'),('T',  'Time Limit Exceeded'))
    user = models.ForeignKey(to=User)
    node = models.ForeignKey(to=Node, null=True, blank=True)
    executable = models.ForeignKey(to=UserFiles, related_name='executables')
    input_file = models.ForeignKey(to=UserFiles, blank=True, null=True, related_name='input_files')
    output_file = models.ForeignKey(to=UserFiles, blank=True, null=True, related_name='output_files')
    time_limit = models.DurationField(default=timedelta(30))
    memory_limit = models.BigIntegerField(default=134217728)
    status = models.CharField(max_length=1, choices=SCHEDULE_STATUS, default='W')
    time_taken = models.DurationField(blank=True, null=True)
    memory_used = models.BigIntegerField(blank=True, null=True)
