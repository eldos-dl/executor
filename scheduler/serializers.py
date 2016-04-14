from rest_framework import serializers


class NodeSerializer(serializers.Serializer):
    ip = serializers.IPAddressField(default='127.0.0.1', required=False)
    port = serializers.IntegerField(default=80)
    host = serializers.BooleanField(required=False, default=False, write_only=True)

    def create(self, validated_data):
        from .models import Node
        is_host = validated_data.pop('host')
        node = Node.objects.get_or_create(**validated_data)[0]
        node.host = is_host
        node.save()
        return node

    def update(self, instance, validated_data):
        instance.ip = validated_data.get('ip', instance.ip)
        instance.port = validated_data.get('port', instance.port)
        instance.host = validated_data.get('host', instance.host)
        instance.save()
        return instance


class StatusSerializer(serializers.Serializer):
    memory_total = serializers.IntegerField()
    memory_available = serializers.IntegerField()
    memory_used_percent = serializers.FloatField()
    cpu_total = serializers.IntegerField()
    cpu_used_percent = serializers.FloatField()
    cpu_idle_percent = serializers.FloatField()
    node = NodeSerializer(many=False)

    def create(self, validated_data):
        from .types import StatusType
        from .models import Status, Node
        node_data = validated_data.pop('node')
        node_data.pop('host')
        node, created = Node.objects.get_or_create(**node_data)
        status = Status.objects.create(node=node, **validated_data)
        return status

        # def update(self, instance, validated_data):
        #     instance.memory_total =


class ScheduleSerializer(serializers.Serializer):
    executable = serializers.IntegerField()
    input_file = serializers.IntegerField()

    time_limit = serializers.DurationField()
    memory_limit = serializers.IntegerField()

    def create(self, validated_data):
        from .models import Schedule
        from .models import UserFiles
        executable_file = UserFiles.objects.get(id=validated_data['executable'])
        input_file = UserFiles.objects.get(id=validated_data['input_file'])
        time_limit = validated_data['time_limit']
        memory_limit = validated_data['time_limit']
        temp = Schedule.objects.create(executable=executable_file, input_file=input_file, time_limit=time_limit,
                                       memory_limit=memory_limit)
        temp.save()
        return temp


class ExecutionSerializer(serializers.Serializer):

    executable_file = serializers.FileField()
    input_file = serializers.FileField()


    time_limit = serializers.DurationField()
    memory_limit = serializers.IntegerField()

    def create(selfself,validated_data):
        from .models import Execution
        files_data = validated_data.pop('files')


