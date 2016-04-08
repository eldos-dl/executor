from rest_framework import serializers


class StatsSerializer(serializers.Serializer):
    memory_total = serializers.IntegerField()
    memory_available = serializers.IntegerField()
    memory_used_percent = serializers.FloatField()
    cpu_count = serializers.IntegerField()
    cpu_used_percent = serializers.FloatField()
    cpu_idle_percent = serializers.FloatField()

    def create(self, validated_data):
        from .types import StatsType
        return StatsType(**validated_data)
