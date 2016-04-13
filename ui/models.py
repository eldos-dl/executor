from __future__ import unicode_literals

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

