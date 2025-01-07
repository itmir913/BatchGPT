import json

from rest_framework import serializers

from api.models import TaskUnitResponse


class TaskUnitResponseSerializer(serializers.ModelSerializer):
    task_unit_id = serializers.IntegerField(source='task_unit.id')  # TaskUnit ID
    unit_index = serializers.IntegerField(source='task_unit.unit_index')  # 작업 단위 인덱스

    class Meta:
        model = TaskUnitResponse
        fields = ['task_unit_id', 'unit_index', 'request_data', 'response_data',
                  'task_response_status']  # response_data 포함

    def to_representation(self, instance):
        """
        response_data 필드를 변환하여 반환합니다.
        """
        # 기본 직렬화 결과 가져오기
        representation = super().to_representation(instance)

        # response_data 가공
        try:
            # JSON 데이터를 로드하고 필요한 값 추출
            json_data = json.loads(representation['response_data'])
            representation['response_data'] = json_data['choices'][0]['message']['content']
        except (KeyError, TypeError, ValueError) as e:
            # 예외 발생 시 기본값 설정
            representation['response_data'] = None

        return representation
