from datetime import timedelta

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
    leader = NodeSerializer(many=False, required=False, allow_null=True)

    def create(self, validated_data):
        from .models import Status, Node
        node_data = validated_data.pop('node')
        leader = None
        if 'leader' in validated_data:
            leader_data = validated_data.pop('leader')
            if leader_data is not None:
                leader_data.pop('host')
                leader, created = Node.objects.get_or_create(**leader_data)
        node_data.pop('host')
        node, created = Node.objects.get_or_create(**node_data)
        status = Status.objects.create(node=node, leader=leader, **validated_data)
        return status


class ExecutionSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    executable_file = serializers.FileField()
    input_file = serializers.FileField()
    time_limit = serializers.DurationField(required=False, default=timedelta(30))
    memory_limit = serializers.IntegerField(required=False, default=134217728)

    def create(self, validated_data):
        from .models import Execution
        execution = Execution.objects.create(**validated_data)
        return execution


class ExecutionResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField(max_length=1)
    time_taken = serializers.DurationField()
    memory_used = serializers.IntegerField(required=False)

    def create(self, validated_data):
        from ui.models import Schedule
        schedule = Schedule.objects.get(id=validated_data['id'])
        schedule.status = validated_data['status']
        schedule.time_taken = validated_data['time_taken']
        if 'memory_used' in validated_data:
            schedule.memory_used = validated_data['memory_used']
        schedule.save()
        return schedule
