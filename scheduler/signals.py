from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile

from .models import Execution, Node
from .types import ExecutionResponseType
import subprocess, os, stat, requests, datetime


# TODO: Notify leader after file execution.
@receiver(post_save, sender=Execution, dispatch_uid="execute")
def run_files(sender, instance, **kwargs):
    if instance.status == 'R':
        executable_path = instance.executable_file.path
        os.chmod(executable_path, os.stat(executable_path).st_mode | stat.S_IEXEC)
        # based on exec file set the command
        command = executable_path
        begin = datetime.datetime.now()
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, err = process.communicate(instance.input_file.read())
        end = datetime.datetime.now()
        time_taken = end - begin
        instance.output_file.save(executable_path.split('/')[-1] + '.out', ContentFile(output))
        instance.status = 'S'
        instance.save()
        leader = Node.objects.get(state='HL')
        status = 'E' if err else 'C'
        files = {"file": (executable_path.split('/')[-1], instance.output_file.file.file)}
        payload = ExecutionResponseType(id=instance.schedule_id, status=status, time_taken=time_taken)
        requests.post(leader.get_http_endpoint() + 'output/', files=files,
                      data=payload.data)
