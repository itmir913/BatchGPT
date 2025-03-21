import logging

from rest_framework import serializers

from api.models import BatchJob
from api.utils.files_processor.file_settings import FileSettings


class BatchJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchJob
        fields = ['title', 'description']  # 필요한 필드만 포함


class BatchJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchJob
        # fields = "__all__"
        fields = ['id', 'created_at', 'updated_at', 'title', 'description', 'file_name', 'batch_job_status']
        read_only_fields = ['id', 'created_at', 'updated_at']  # 읽기 전용 필드 지정

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['batch_job_status'] = instance.get_batch_job_status_display()
        return representation


class BatchJobConfigSerializer(serializers.ModelSerializer):
    file_type = serializers.SerializerMethodField()  # 파일 이름을 위한 커스텀 필드
    total_size = serializers.SerializerMethodField()  # total_size 필드 추가

    class Meta:
        model = BatchJob
        # fields = "__all__"
        fields = ['id', 'created_at', 'updated_at',
                  'title', 'description',
                  'file_name', 'file_type', 'total_size',
                  'configs', 'batch_job_status']
        read_only_fields = ['id', 'created_at', 'updated_at']  # 읽기 전용 필드 지정

    def get_file_type(self, obj):
        if obj.file:
            return FileSettings.get_file_extension(obj.file.name)
        return None

    def get_total_size(self, obj):
        if obj.file:
            try:
                return obj.get_size()
            except ValueError as e:
                logger = logging.getLogger(__name__)
                logger.log(logging.ERROR, f"API: Unsupported File Type: {str(e)}")
                raise ValueError(f"Unsupported File Type: {str(e)}")
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.log(logging.ERROR, f"API: Internal Server Error: {str(e)}")
                raise ValueError(f"Internal Server Error: {str(e)}")
        return 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['batch_job_status'] = instance.get_batch_job_status_display()
        return representation
