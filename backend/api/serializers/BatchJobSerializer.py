from rest_framework import serializers

from job.models import BatchJob


class BatchJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchJob
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']  # 읽기 전용 필드 지정


class BatchJobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchJob
        fields = ['title', 'description']  # 필요한 필드만 포함
