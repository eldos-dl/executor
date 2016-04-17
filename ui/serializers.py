from datetime import timedelta

from rest_framework import serializers


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
    size = serializers.SerializerMethodField(required=False)
    type = serializers.ChoiceField(choices=[('E', 'exec'), ('I', 'io')], required=False)
    last_updated = serializers.DateTimeField(required=False)

    def get_name(self, instance):
        return instance.file.name

    def get_size(self, instance):
        return instance.file.size

    def create(self, validated_data):
        from .models import UserFiles, User
        try:
            user = User.objects.get(id=self.context.get('user_id'))
            user_file = UserFiles.objects.get(id=validated_data['id'], user=user)
            return user_file
        except:
            raise

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


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
    from scheduler.serializers import NodeSerializer
    id = serializers.IntegerField()
    status = serializers.CharField(max_length=1)
    time_taken = serializers.DurationField(allow_null=True)
    memory_used = serializers.IntegerField(allow_null=True)
    node = NodeSerializer(many=False, allow_null=True)
    output_file_id = serializers.IntegerField(allow_null=False, required=False)


class ExecutionRequestSerializer(serializers.Serializer):
    schedule_id = serializers.IntegerField()
    time_limit = serializers.DurationField(required=False, default=timedelta(30))
    memory_limit = serializers.IntegerField(required=False, default=134217728)


class DiffRequestSerializer(serializers.Serializer):
    from .models import UserFiles
    old_source = serializers.PrimaryKeyRelatedField(queryset=UserFiles.objects.all())
    new_source = serializers.PrimaryKeyRelatedField(queryset=UserFiles.objects.all())

    def get_files(self):
        from .models import User
        validated_data = self.validated_data
        user = User.objects.get(id=self.context.get('user_id'))
        if validated_data['old_source'].user == user and validated_data['new_source'].user == user:
            old_file = validated_data['old_source'].file.read()
            new_file = validated_data['new_source'].file.read()
            return old_file, new_file
        else:
            raise


class UserFileRequestSerializer(serializers.Serializer):
    from .models import UserFiles
    file = serializers.PrimaryKeyRelatedField(queryset=UserFiles.objects.all())


class DiffSerializer(serializers.Serializer):
    delta = serializers.IntegerField()
    line = serializers.CharField(allow_blank=True, trim_whitespace=False)
