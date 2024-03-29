import subprocess
import os
import stat
import datetime

from django.db.models.signals import post_save

from django.dispatch import receiver

from django.core.files.base import ContentFile
import requests

from .models import Execution, Node
from .types import ExecutionResponseType
from .serializers import ExecutionResponseSerializer
import signal

from .utils import Alarm, alarm_handler


# TODO: Notify leader after file execution.
@receiver(post_save, sender=Execution, dispatch_uid="execute")
def run_files(sender, instance, **kwargs):
    if instance.status == 'R':
        try:
            executable_path = instance.executable_file.path
            os.chmod(executable_path, os.stat(executable_path).st_mode | stat.S_IEXEC)
            # based on exec file set the command
            command = executable_path
            begin = datetime.datetime.now()
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            instance.input_file.file.seek(0)
            input_data = instance.input_file.file.read()
            output, err = process.communicate(input_data)
            end = datetime.datetime.now()
            time_taken = end - begin
            instance.status = 'S'
            output_name = executable_path.split('/')[-1][1:] + '.out'
            print output_name
            instance.output_file.save(output_name, ContentFile(output))
            instance.save()
            leader = Node.objects.get(state='HL')
            status = 'E' if err else 'C'
            print status
            files = {"file": (output_name, instance.output_file.file.file)}
            payload = ExecutionResponseSerializer(
                ExecutionResponseType(id=instance.schedule_id, status=status, time_taken=time_taken))
            response = requests.post(leader.get_http_endpoint() + 'output/', files=files,
                                     data=payload.data)
            print response
        except:
            instance.status = 'F'
            instance.save()
