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

