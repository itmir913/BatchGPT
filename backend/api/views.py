import logging
import os

from django.core.exceptions import ValidationError
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_202_ACCEPTED, HTTP_404_NOT_FOUND
from rest_framework.views import APIView

from api.models import BatchJob, TaskUnitStatus, BatchJobStatus
from api.models import TaskUnit, TaskUnitResponse
from api.serializers.BatchJobSerializer import BatchJobSerializer, BatchJobCreateSerializer, BatchJobConfigSerializer
from api.utils.file_settings import FileSettings
from api.utils.generate_prompt import get_openai_result
from api.utils.job_status_utils import get_task_status_counts
from backend import settings
from tasks.queue_batch_job_process import process_batch_job

logger = logging.getLogger(__name__)


class UserBatchJobsView(APIView):
    """
    View to handle user's batch jobs.
    - GET: Retrieve all batch jobs for the authenticated user.
    - POST: Create a new batch job for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all batch jobs for the authenticated user.
        현재 사용자의 모든 BatchJob 목록을 반환하는 기능
        """
        logger.log(logging.DEBUG, f"{request.user.email} has requested the BatchJob list.")

        batch_jobs = BatchJob.objects.filter(user=request.user).order_by('-updated_at')
        serializer = BatchJobSerializer(batch_jobs, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        사용자가 BathJob을 생성하는 기능
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = BatchJobCreateSerializer(data=request.data)
        if serializer.is_valid():
            batch_job = serializer.save(user=request.user)
            return Response(
                {"message": "BatchJob created successfully", "id": batch_job.id},
                status=HTTP_201_CREATED
            )
        return Response({"message": serializer.errors}, status=HTTP_400_BAD_REQUEST)


class BatchJobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        """
        클라이언트 측으로 BatchJob의 제목과 설명을 반환하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        serializer = BatchJobSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, batch_id):
        """
        사용자가 BatchJob의 제목과 설명을 업데이트하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        serializer = BatchJobSerializer(batch_job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=HTTP_200_OK)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, batch_id):
        """
        사용자가 자신이 생성한 BatchJob을 삭제하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        batch_job.delete()
        return Response(status=HTTP_204_NO_CONTENT)


class BatchJobFileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, batch_id):
        """
        사용자가 서버 측으로 파일을 업로드하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        file = request.FILES.get('file')
        if not file:
            return Response(
                {"error": "No file provided."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            total_size = FileSettings.get_size(file)
            if total_size <= 0:
                raise ValidationError(
                    "The file cannot be read because its size is 0 or less."
                    "It seems to be an invalid file. Please try with a different file.")

            batch_job.file = file
            batch_job.file_name = file.name
            batch_job.configs = {}  # 파일이 새로 업로드 되었다면, 기존 설정 초기화
            batch_job.set_status(BatchJobStatus.UPLOADED)

            batch_job.save()
        except ValidationError as e:
            return Response(
                {"error": ("The BatchJob cannot be modified at this time."
                           "Please check again to see if the task is running.")},
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
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        """
        현재 BatchJob의 구성 설정을 반환하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        if batch_job.batch_job_status in [BatchJobStatus.IN_PROGRESS]:
            # 현재 BatchJob의 설정을 반환할 때마다 진행중인 BatchJob의 Status 갱신
            if TaskUnit.objects.filter(batch_job=batch_job).count() > 0:
                pending, in_progress, fail = get_task_status_counts(batch_id)

                if pending > 0 or in_progress > 0:
                    pass
                elif fail > 0:
                    batch_job.set_status(BatchJobStatus.FAILED)
                    batch_job.save()
                else:
                    batch_job.set_status(BatchJobStatus.COMPLETED)
                    batch_job.save()

        serializer = BatchJobConfigSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, batch_id):
        """
        사용자가 결정한 BatchJob Config을 갱신 및 업데이트하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)
        data = request.data

        work_unit = int(data.get('work_unit', 1))
        prompt = data.get('prompt', "")
        gpt_model = data.get('gpt_model', 'gpt-4o-mini')
        selected_headers = data.get('selected_headers', None)

        if prompt is None:
            return Response({'error': 'No prompt provided.'}, status=HTTP_400_BAD_REQUEST)

        try:
            total_size = batch_job.get_size() if batch_job.file else 0
            if work_unit > total_size:
                return Response({'error': 'The work unit exceeds the total size.'}, status=HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'error': f"File processing error: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=HTTP_500_INTERNAL_SERVER_ERROR,
            )

        current_config = batch_job.configs or {}

        current_config['work_unit'] = work_unit
        current_config['prompt'] = prompt
        current_config['gpt_model'] = gpt_model
        current_config['selected_headers'] = selected_headers

        batch_job.configs = current_config
        batch_job.set_status(BatchJobStatus.CONFIGS)

        batch_job.save()
        serializer = BatchJobConfigSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)


class BatchJobPreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        """
        사용자가 업로드한 CSV, PDF 파일의 일부를 제공하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            preview = batch_job.get_preview()
            return JsonResponse(preview, safe=False, status=HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"The preview cannot be fetched."
                          f"An error occurred while processing the file on the server.: {str(e)}"},
                status=HTTP_400_BAD_REQUEST,
            )

    def post(self, request, batch_id):
        """
        사용자가 CSV의 헤더, 혹은 PDF의 작업 단위를 결정한 후
        GPT 결과 미리보기를 요청하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_object_or_404(BatchJob, id=batch_id)

        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            data = request.data
            prompt = data.get('prompt', None)

            if prompt is None:
                return Response(
                    {"error": "The request is invalid as the prompt is empty."},
                    status=HTTP_400_BAD_REQUEST,
                )
            else:
                batch_job.configs['prompt'] = prompt
                batch_job.configs['selected_headers'] = data.get('selected_headers', None)
                batch_job.save()

            file = batch_job.file
            file_path = os.path.join(settings.BASE_DIR, file.path)
            json_formatted = []

            processor = FileSettings.get_file_processor(FileSettings.get_file_extension(file_path))
            for index, prompt in enumerate(processor.process(batch_job.id, file_path), start=1):
                if str(prompt).strip():
                    task_unit, created = TaskUnit.objects.update_or_create(
                        batch_job=batch_job,
                        unit_index=index,
                        defaults={
                            'text_data': prompt,
                            'file_data': None,
                            'task_unit_status': TaskUnitStatus.PENDING,
                            'latest_response': None,
                        }
                    )

                    json_formatted.append({
                        "task_unit_id": task_unit.id,
                        "prompt": prompt,
                        "result": "",
                        "status": TaskUnitStatus.PENDING
                    })

                if index >= 3:
                    break  # Stop after 3 iterations

            batch_job.set_status(BatchJobStatus.CONFIGS)
            batch_job.save()

            return JsonResponse(json_formatted, safe=False, status=HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"cannot retrive preview: {str(e)}"},
                status=HTTP_400_BAD_REQUEST,
            )


class BatchJobSupportFileType(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        클라이언트 측에서 업로드 가능한 파일 타입을 요청하면 반환하는 기능
        :param request:
        :return:
        """
        return Response(FileSettings.FILE_TYPES, status=HTTP_200_OK)


class TaskUnitPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class TaskUnitResponsePagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class TaskUnitResponseListAPIView(ListAPIView):
    pagination_class = TaskUnitResponsePagination

    def get_queryset(self):
        batch_id = self.kwargs.get('batch_id')

        # TaskUnit 모델에서 최신 응답을 가져오는 방식으로 수정
        queryset = TaskUnit.objects.filter(batch_job_id=batch_id).annotate(
            task_response_status=F('latest_response__task_response_status'),
            request_data=F('latest_response__request_data'),
            response_data=F('latest_response__response_data'),
            error_message=F('latest_response__error_message'),
            processing_time=F('latest_response__processing_time'),
        ).order_by('unit_index')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        # 결과를 직렬화
        results = [
            {
                "task_unit_id": item.id,
                "task_unit_status": item.get_task_unit_status_display(),
                "unit_index": item.unit_index,
                "request_data": item.text_data if item.text_data is not None else item.file_data,
                "response_data": get_openai_result(item.response_data),
                "error_message": item.error_message,
                "processing_time": item.processing_time,
            }
            for item in page
        ]

        return self.get_paginated_response(results)


class TaskUnitStatusView(APIView):
    # TODO 이름 바꾸기
    permission_classes = [IsAuthenticated]

    status_code_map = {
        TaskUnitStatus.PENDING: HTTP_202_ACCEPTED,
        TaskUnitStatus.IN_PROGRESS: HTTP_202_ACCEPTED,
        TaskUnitStatus.COMPLETED: HTTP_201_CREATED,
        TaskUnitStatus.FAILED: HTTP_400_BAD_REQUEST,
    }

    def get(self, request, batch_id, task_unit_id):
        """
        하나의 작업 단위에 대하여 진행 상황을 실시간 갱신하고자
        클라이언트 측에서 현재 상태를 요청하는 기능
        :param request:
        :param batch_id:
        :param task_unit_id:
        :return:
        """
        try:
            task_unit = get_object_or_404(TaskUnit, id=task_unit_id)

            if task_unit.latest_response is None:
                return JsonResponse({"error": "Task response not found"}, status=HTTP_404_NOT_FOUND)

            task_unit_result = get_object_or_404(TaskUnitResponse, id=task_unit.latest_response.id)
            status = task_unit_result.task_response_status

            response_data = {
                "batch_id": task_unit.batch_job_id,
                "task_unit_id": task_unit_id,
                "status": task_unit_result.get_task_response_status_display()
            }

            if status == TaskUnitStatus.COMPLETED:
                json_data = task_unit_result.response_data
                response_data["response_data"] = json_data['choices'][0]['message']['content']

            return JsonResponse(response_data, status=self.status_code_map.get(status, HTTP_500_INTERNAL_SERVER_ERROR))

        except TaskUnit.DoesNotExist:
            return JsonResponse({"error": "Task unit not found"}, status=HTTP_404_NOT_FOUND)

        except TaskUnitResponse.DoesNotExist:
            return JsonResponse({"error": "Task response not found"}, status=HTTP_404_NOT_FOUND)


class BatchJobRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, batch_id):
        """작업을 시작"""
        try:

            batch_job = get_object_or_404(BatchJob, id=batch_id)

            batch_job.set_status(BatchJobStatus.PENDING)
            batch_job.save()

            process_batch_job.apply_async(args=[batch_job.id])

            serializer = BatchJobConfigSerializer(batch_job)
            return Response(serializer.data, status=HTTP_200_OK)
        except BatchJob.DoesNotExist:
            return Response(
                {"error": "BatchJob not found."},
                status=HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=HTTP_400_BAD_REQUEST
            )

    def get(self, request, batch_id):
        """작업 상태 점검"""
        try:
            batch_job = BatchJob.objects.get(id=batch_id)

            return Response(
                {"id": batch_id,
                 "batch_job_status": batch_job.get_batch_job_status_display()},
                status=HTTP_200_OK
            )

        except BatchJob.DoesNotExist:
            return Response(
                {"error": "BatchJob not found."},
                status=HTTP_404_NOT_FOUND
            )
