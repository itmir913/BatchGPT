import os

from rest_framework import serializers

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
