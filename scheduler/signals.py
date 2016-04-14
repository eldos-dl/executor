from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Execution


# TODO: Add file execution code here.
@receiver(post_save, sender=Execution, dispatch_uid="execute")
def run_files(sender, instance, **kwargs):
    pass
