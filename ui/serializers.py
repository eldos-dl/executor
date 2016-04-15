from rest_framework import serializers
from datetime import timedelta

class FileSerializer(serializers.Serializer):
    file = serializers.FileField(allow_empty_file=True)
    type = serializers.ChoiceField(choices=[('E', 'exec'), ('I', 'io')], default='E')


class UserFileSerializer(serializers.Serializer):
    files = FileSerializer(many=True)

    def create(self, validated_data):
        from django.contrib.auth.models import User
        from .models import UserFiles

        files_data = validated_data.pop('files')
        user = User.objects.get(id=self.context.get('user_id'))
        for file_data in files_data:
            last = UserFiles.objects.create(user=user, file=file_data['file'], type=file_data['type'],
                                            name=file_data['file'].name)
        return last


class FileDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    size = serializers.SerializerMethodField()
    type = serializers.ChoiceField(choices=[('E', 'exec'), ('I', 'io')])
    last_updated = serializers.DateTimeField()

    def get_name(self, instance):
        return instance.file.name

    def get_size(self, instance):
        return instance.file.size


class ScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        from .models import Schedule
        model = Schedule
        fields = ('executable', 'input_file', 'time_limit', 'memory_limit')

    def create(self, validated_data):
        from .models import Schedule, User
        try:
            user = User.objects.get(id=self.context.get('user_id'))
            if validated_data['executable'].user == user and validated_data['input_file'].user == user:
                schedule = Schedule.objects.create(user=user, **validated_data)
                return schedule
            else:
                raise
        except:
            raise


class ScheduleResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField(max_length=1)
    time_taken = serializers.DurationField(allow_null=True)
    memory_used = serializers.IntegerField(allow_null=True)


class ExecutionRequestSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    time_limit = serializers.DurationField(required=False, default=timedelta(30))
    memory_limit = serializers.IntegerField(required=False, default=134217728)
