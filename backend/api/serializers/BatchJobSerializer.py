import os

from rest_framework import serializers

from api.utils.file_settings import FileSettings
from job.models import BatchJob


class BatchJobSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()  # 파일 이름을 위한 커스텀 필드

    class Meta:
        model = BatchJob
        # fields = "__all__"
        fields = ['id', 'created_at', 'updated_at', 'title', 'description', 'file_name']
        read_only_fields = ['id', 'created_at', 'updated_at']  # 읽기 전용 필드 지정

    def get_file_name(self, obj):
        if obj.file:
            # 전체 경로에서 파일 이름 추출
            name = os.path.basename(obj.file.name)
            # "file_" 접두사 제거
            return name.replace("file_", "", 1)  # 첫 번째 인스턴스만 제거
        return None  # 파일이 없을 경우 None 반환


class BatchJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchJob
        fields = ['title', 'description']  # 필요한 필드만 포함


class BatchJobConfigSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()  # 파일 이름을 위한 커스텀 필드
    file_type = serializers.SerializerMethodField()  # 파일 이름을 위한 커스텀 필드
    total_size = serializers.SerializerMethodField()  # total_size 필드 추가

    class Meta:
        model = BatchJob
        # fields = "__all__"
        fields = ['id', 'created_at', 'updated_at',
                  'title', 'description',
                  'file_name', 'file_type', 'total_size',
                  'config']
        read_only_fields = ['id', 'created_at', 'updated_at']  # 읽기 전용 필드 지정

    def get_file_name(self, obj):
        if obj.file:
            # 전체 경로에서 파일 이름 추출
            name = os.path.basename(obj.file.name)
            # "file_" 접두사 제거
            return name.replace("file_", "", 1)  # 첫 번째 인스턴스만 제거
        return None  # 파일이 없을 경우 None 반환

    def get_file_type(self, obj):
        if obj.file:
            return FileSettings.get_file_extension(obj.file.name)
        return None

    def get_total_size(self, obj):
        if obj.file:
            try:
                return obj.get_file_total_size()
            except ValueError as e:
                raise ValueError("Unsupported File Type")
        return 0
