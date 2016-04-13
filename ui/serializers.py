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
            print file_data['file']
            print file_data['file'].name
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
