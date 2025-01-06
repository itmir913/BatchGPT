import json
import logging

from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from api.serializers.BatchJobSerializer import BatchJobSerializer, BatchJobCreateSerializer, BatchJobConfigSerializer
from api.utils.file_settings import FileSettings
from api.utils.generate_prompt import get_prompt
from job.models import BatchJob


class UserBatchJobsView(APIView):
    """
    View to handle user's batch jobs.
    - GET: Retrieve all batch jobs for the authenticated user.
    - POST: Create a new batch job for the authenticated user.
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request):
        """
        Retrieve all batch jobs for the authenticated user.
        """
        # 현재 로그인된 사용자와 연결된 BatchJob 가져오기
        batch_jobs = BatchJob.objects.filter(user=request.user).order_by('-updated_at')
        serializer = BatchJobSerializer(batch_jobs, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    """
    BatchJob 생성 API 엔드포인트
    """

    def post(self, request, *args, **kwargs):
        # 요청 데이터를 직렬화
        serializer = BatchJobCreateSerializer(data=request.data)
        if serializer.is_valid():  # 데이터 검증
            # 현재 요청의 사용자와 함께 저장
            batch_job = serializer.save(user=request.user)
            return Response(
                {"message": "BatchJob created successfully", "id": batch_job.id},
                status=HTTP_201_CREATED
            )
        return Response({"message": serializer.errors}, status=HTTP_400_BAD_REQUEST)


class BatchJobDetailView(APIView):
    """
    API 엔드포인트: 특정 BatchJob 정보를 반환
    - URL: /api/batch-jobs/<int:id>/
    - 메서드: GET
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request, batch_id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        # 현재 요청한 사용자가 소유자인지 확인
        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        # 직렬화하여 응답 반환
        serializer = BatchJobSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, batch_id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        # 현재 요청한 사용자가 소유자인지 확인
        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        # 직렬화하여 데이터 업데이트
        serializer = BatchJobSerializer(batch_job, data=request.data, partial=True)  # partial=True로 부분 업데이트 허용
        if serializer.is_valid():
            serializer.save()  # 변경 사항 저장
            return Response(status=HTTP_200_OK)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, batch_id):
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        batch_job.delete()  # BatchJob 객체 삭제
        return Response(status=HTTP_204_NO_CONTENT)  # 성공적으로 삭제되었음을 알림


class BatchJobFileUploadView(APIView):
    """
    API 엔드포인트: 특정 BatchJob에 파일 업로드
    - URL: /api/batch-jobs/{id}/upload/
    - 메서드: PATCH
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def patch(self, request, batch_id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        # 현재 요청한 사용자가 소유자인지 확인
        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        # 파일이 요청에 포함되어 있는지 확인
        file = request.FILES.get('file')
        if not file:
            return Response(
                {"error": "No file provided."},
                status=HTTP_400_BAD_REQUEST,
            )

        # 파일 저장
        try:
            total_size = FileSettings.get_total_size_for_file_types(file)
            if total_size <= 0:
                raise ValidationError(
                    "The file cannot be read because its size is 0 or less."
                    "It seems to be an invalid file. Please try with a different file.")

            batch_job.file = file
            batch_job.file_name = file.name
            batch_job.config = {}

            batch_job.save()
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = BatchJobConfigSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)


class BatchJobConfigView(APIView):
    """
    API 엔드포인트: 특정 BatchJob 정보를 반환
    - URL: /api/batch-jobs/<int:id>/preview/
    - 메서드: GET
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request, batch_id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        # 현재 요청한 사용자가 소유자인지 확인
        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        serializer = BatchJobConfigSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)
        # return Response(
        #     {
        #         "id": batch_job.id,
        #         "title": batch_job.title,
        #         "description": batch_job.description,
        #         "file_name": batch_job.file.name if batch_job.file else None,
        #         "file_type": FileSettings.get_file_extension(batch_job.file.name) if batch_job.file.name else None,
        #         "total_size": batch_job.get_total_size() if batch_job.file else -1,
        #         "config": batch_job.config if batch_job.config else None,
        #         "created_at": batch_job.created_at,
        #         "updated_at": batch_job.updated_at,
        #     },
        #     status=HTTP_200_OK,
        # )

    def patch(self, request, batch_id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        # 클라이언트로부터 JSON 데이터 받기
        data = request.data
        work_unit = int(data.get('work_unit', 1))
        prompt = data.get('prompt', None)
        gpt_model = data.get('gpt_model', 'gpt-4o-mini')
        selected_headers = data.get('selected_headers', None)

        if prompt is None:
            return Response({'error': 'No prompt provided.'}, status=HTTP_400_BAD_REQUEST)

        # 파일 존재 여부 및 사이즈 확인
        try:
            total_size = batch_job.get_file_total_size() if batch_job.file else 0
        except ValueError as e:
            return Response({'error': f"File processing error: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if work_unit > total_size:
            return Response({'error': 'The work unit exceeds the total size.'}, status=HTTP_400_BAD_REQUEST)

        # 기존 config 데이터 가져오기
        current_config = batch_job.config or {}

        # 새로운 설정 추가 또는 업데이트
        current_config['work_unit'] = work_unit
        current_config['prompt'] = prompt
        current_config['gpt_model'] = gpt_model
        current_config['selected_headers'] = selected_headers

        # 수정된 config 저장
        batch_job.config = current_config
        batch_job.save()

        serializer = BatchJobConfigSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)


class BatchJobPreView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request, batch_id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        # 현재 요청한 사용자가 소유자인지 확인
        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            preview = batch_job.get_file_preview()
            return JsonResponse(preview, safe=False, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"The preview cannot be fetched."
                          f"An error occurred while processing the file on the server.: {str(e)}"},
                status=HTTP_400_BAD_REQUEST,
            )

    def post(self, request, batch_id):
        logger = logging.getLogger(__name__)

        batch_job = get_object_or_404(BatchJob, id=batch_id)

        # 현재 요청한 사용자가 소유자인지 확인
        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            data = request.data
            prompt = data.get('prompt', None)
            selected_headers = data.get('selected_headers', None)

            if prompt is None or selected_headers is None:
                return Response(
                    {"error": "The request is invalid as the prompt is empty or no headers were selected."},
                    status=HTTP_400_BAD_REQUEST,
                )

            config = batch_job.config
            work_unit = int(config['work_unit'])
            gpt_model = config['gpt_model']

            preview = batch_job.get_file_preview()
            preview = json.loads(preview)

            logger.error("preview")
            logger.error(preview)

            filtered_preview = [
                {key: str(value) for key, value in item.items() if key in selected_headers}
                for item in preview
            ]

            logger.error("filtered_preview")
            logger.error(filtered_preview)

            generate_prompt = [get_prompt(prompt, item) for item in filtered_preview]
            json_formatted = [{
                "prompt": item,
                "result": "test"
            } for item in generate_prompt]

            logger.error("generate_prompt")
            logger.error(generate_prompt)

            return JsonResponse(json_formatted, safe=False, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"cannot retrive preview: {str(e)}"},
                status=HTTP_400_BAD_REQUEST,
            )


class BatchJobSupportFileType(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request):
        return Response(FileSettings.FILE_TYPES, status=HTTP_200_OK)
