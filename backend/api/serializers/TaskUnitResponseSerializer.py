from rest_framework import serializers


class FlattenedTaskUnitResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    unit_index = serializers.IntegerField()
    task_unit_status = serializers.CharField()
    task_response_status = serializers.CharField(allow_null=True)
    request_data = serializers.JSONField(allow_null=True)
    response_data = serializers.JSONField(allow_null=True)
    error_message = serializers.CharField(allow_null=True)
    processing_time = serializers.FloatField(allow_null=True)
