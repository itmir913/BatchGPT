import logging
import os

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_202_ACCEPTED, HTTP_404_NOT_FOUND, HTTP_423_LOCKED
from rest_framework.views import APIView

from api.models import BatchJob, TaskUnitStatus, BatchJobStatus
from api.models import TaskUnit, TaskUnitResponse
from api.serializers.BatchJobSerializer import BatchJobSerializer, BatchJobCreateSerializer, BatchJobConfigSerializer
from api.utils.cache_keys import batch_job_cache_key, task_unit_cache_key, \
    task_unit_response_cache_key, CACHE_TIMEOUT_BATCH_JOB, CACHE_TIMEOUT_TASK_UNIT, CACHE_TIMEOUT_TASK_UNIT_RESPONSE, \
    get_cache_or_database
from api.utils.files_processor.file_settings import FileSettings
from api.utils.files_processor.pdf_processor import PDFProcessMode
from api.utils.gpt_processor.gpt_settings import get_gpt_processor
from api.utils.job_status_utils import get_task_status_counts
from backend import settings
from tasks.queue_batch_job_process import process_batch_job

logger = logging.getLogger(__name__)


def updateBatchJobStatus(batch_job):
    if batch_job.batch_job_status in [BatchJobStatus.IN_PROGRESS]:
        if TaskUnit.objects.filter(batch_job=batch_job).count() > 0:
            pending, in_progress, fail = get_task_status_counts(batch_job.id)

            if pending > 0 or in_progress > 0:
                pass
            elif fail > 0:
                logger.log(logging.DEBUG, f"API: The job with ID {batch_job.id} has been marked as Failed.")
                batch_job.set_status(BatchJobStatus.FAILED)
                batch_job.save()
            else:
                logger.log(logging.DEBUG, f"API: The job with ID {batch_job.id} has been marked as Completed.")
                batch_job.set_status(BatchJobStatus.COMPLETED)
                batch_job.save()


@method_decorator(login_required, name='dispatch')
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
        logger.log(logging.DEBUG, f"API: {request.user.email} has requested the BatchJob list.")

        batch_jobs_in_progress = BatchJob.objects.filter(
            user=request.user,
            batch_job_status=BatchJobStatus.IN_PROGRESS
        )

        for batch_job in batch_jobs_in_progress:
            updateBatchJobStatus(batch_job)

        batch_jobs = BatchJob.objects.filter(user=request.user).order_by('-updated_at')
        serializer = BatchJobSerializer(batch_jobs, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


@method_decorator(login_required, name='dispatch')
class CreateBatchJobsView(APIView):
    """
    View to handle user's batch jobs.
    - GET: Retrieve all batch jobs for the authenticated user.
    - POST: Create a new batch job for the authenticated user.
    """
    permission_classes = [IsAuthenticated]

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
            logger.log(logging.DEBUG, f"API: BatchJob created successfully.")
            return Response(
                {"message": "BatchJob created successfully", "id": batch_job.id},
                status=HTTP_201_CREATED
            )
        logger.log(logging.ERROR, f"API: BatchJob create failed: {serializer.errors}")
        return Response({"message": serializer.errors}, status=HTTP_400_BAD_REQUEST)


@method_decorator(login_required, name='dispatch')
class BatchJobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        """
        클라이언트 측으로 BatchJob의 제목과 설명을 반환하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=batch_id,
            cache_key=batch_job_cache_key(batch_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        if batch_job.user != request.user:
            logger.log(logging.ERROR, f"API: You({request.user.email}) do not have permission to access this resource.")
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
        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=batch_id,
            cache_key=batch_job_cache_key(batch_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        if batch_job.user != request.user:
            logger.log(logging.ERROR, f"API: You({request.user.email}) do not have permission to access this resource.")
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        serializer = BatchJobSerializer(batch_job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.log(logging.DEBUG, f"API: {request.user.id} is Successfully updated BatchJob.")
            return Response(status=HTTP_200_OK)

        logger.log(logging.ERROR, f"API: Failed to update BatchJob: {serializer.errors}")
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, batch_id):
        """
        사용자가 자신이 생성한 BatchJob을 삭제하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=batch_id,
            cache_key=batch_job_cache_key(batch_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        if batch_job.user != request.user:
            logger.log(logging.ERROR, f"API: You({request.user.email}) do not have permission to access this resource.")
            return Response(
                {"error": "You do not have permission to delete this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        batch_job.delete()
        logger.log(logging.DEBUG, f"API: {request.user.email} has successfully deleted BatchJob with ID {batch_id}.")
        return Response(status=HTTP_204_NO_CONTENT)


@method_decorator(login_required, name='dispatch')
class BatchJobFileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, batch_id):
        """
        사용자가 서버 측으로 파일을 업로드하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=batch_id,
            cache_key=batch_job_cache_key(batch_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        if batch_job.user != request.user:
            logger.log(logging.ERROR, f"API: You({request.user.email}) do not have permission to access this resource.")
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        if batch_job.batch_job_status in [BatchJobStatus.PENDING, BatchJobStatus.IN_PROGRESS,
                                          BatchJobStatus.COMPLETED, BatchJobStatus.FAILED]:
            logger.log(logging.ERROR,
                       f"API: For safety reasons, file modifications are not allowed once a batch job has been executed. "
                       f"To work with a new file, please create a new batch job.")
            return Response(
                {"error": "For safety reasons, file modifications are not allowed once a batch job has been executed. "
                          "To work with a new file, please create a new batch job."},
                status=HTTP_423_LOCKED,
            )

        file = request.FILES.get('file')
        if not file:
            logger.log(logging.ERROR, f"API: No file provided.")
            return Response(
                {"error": "No file provided."},
                status=HTTP_400_BAD_REQUEST,
            )

        try:
            total_size = FileSettings.get_size(file)
            if total_size <= 0:
                logger.log(logging.ERROR, f"API: The file cannot be read because its size is 0 or less."
                                          f"It seems to be an invalid file. Please try with a different file.")
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


@method_decorator(login_required, name='dispatch')
class BatchJobConfigView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        """
        현재 BatchJob의 구성 설정을 반환하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=batch_id,
            cache_key=batch_job_cache_key(batch_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        if batch_job.user != request.user:
            logger.log(logging.ERROR, f"API: You({request.user.email}) do not have permission to access this resource.")
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        updateBatchJobStatus(batch_job)

        serializer = BatchJobConfigSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)

    def patch(self, request, batch_id):
        """
        사용자가 결정한 BatchJob Config을 갱신 및 업데이트하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=batch_id,
            cache_key=batch_job_cache_key(batch_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        updated_data = request.data

        if batch_job.batch_job_status in [BatchJobStatus.PENDING, BatchJobStatus.IN_PROGRESS]:
            logger.log(logging.ERROR, f"API: You cannot change the settings because it is already in operation.")
            return Response(
                {"error": "Warning: You cannot change the settings because it is already in operation."},
                status=HTTP_423_LOCKED,
            )

        current_data = batch_job.configs or {}
        current_data.update(updated_data)

        batch_job.configs = current_data
        batch_job.set_status(BatchJobStatus.CONFIGS)
        batch_job.save()

        serializer = BatchJobConfigSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)


@method_decorator(login_required, name='dispatch')
class BatchJobPreView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, batch_id):
        """
        사용자가 업로드한 CSV, PDF 파일의 일부를 제공하는 기능
        :param request:
        :param batch_id:
        :return:
        """
        batch_job = get_cache_or_database(
            model=BatchJob,
            primary_key=batch_id,
            cache_key=batch_job_cache_key(batch_id),
            timeout=CACHE_TIMEOUT_BATCH_JOB,
        )

        if batch_job.user != request.user:
            logger.log(logging.ERROR, f"API: You({request.user.email}) do not have permission to access this resource.")
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        try:
            work_unit = batch_job.configs.get('work_unit', 1)
            pdf_mode = batch_job.configs.get('pdf_mode', PDFProcessMode.TEXT)

            file = batch_job.file
            file_path = os.path.join(settings.BASE_DIR, file.path)

            processor = FileSettings.get_file_processor(FileSettings.get_file_extension(file_path))
            preview = processor.get_preview(file_path, work_unit=work_unit, pdf_mode=pdf_mode)

            logger.log(logging.DEBUG,
                       f"API: The file preview was successfully returned for the user {request.user.email}.")
            return JsonResponse(preview, safe=False, status=HTTP_200_OK)
        except Exception as e:
            logger.log(logging.ERROR, f"API: The preview cannot be fetched: {str(e)}")
            return Response(
                {"error": f"The preview cannot be fetched: {str(e)}"},
                status=HTTP_400_BAD_REQUEST,
            )


@method_decorator(login_required, name='dispatch')
class BatchJobSupportFileType(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 60), name='get')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """
        클라이언트 측에서 업로드 가능한 파일 타입을 요청하면 반환하는 기능
        :param request:
        :return:
        """
        return Response(FileSettings.FILE_TYPES, status=HTTP_200_OK)


@method_decorator(login_required, name='dispatch')
class BatchJobSupportPDFMode(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(60 * 60), name='get')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """
        클라이언트 측에서 PDF Mode를 요청하면 반환하는 기능
        :param request:
        :return:
        """
        descriptions = PDFProcessMode.get_descriptions()
        modes = [{"key": mode.value, "description": descriptions[mode.value]} for mode in PDFProcessMode]
        return JsonResponse({"modes": modes})


class TaskUnitResponsePagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


@method_decorator(login_required, name='dispatch')
class TaskUnitResponseListAPIView(ListAPIView):
    pagination_class = TaskUnitResponsePagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        batch_id = self.kwargs.get('batch_id')

        queryset = (
            TaskUnit.objects
            .filter(batch_job_id=batch_id)
            .select_related("latest_response")  # latest_response 조인을 최적화
            .prefetch_related("files")  # 수정된 부분: related_name 'files' 사용
            .only("id", "unit_index", "text_data", "has_files", "task_unit_status", "latest_response")
            .order_by("unit_index")
        )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        # 결과를 직렬화
        results = []
        for item in page:
            latest_response = item.latest_response  # select_related로 인해 별도 쿼리 없이 접근 가능

            request_data = {
                "prompt": item.text_data,
                "has_files": item.has_files,
            }

            if item.has_files:
                request_data["files_data"] = [
                    task_unit_file.base64_image_data for task_unit_file in item.files.all()  # 수정된 부분
                ]

            response = latest_response.response_data if latest_response else None
            gpt_processor = get_gpt_processor(company=response.get('Company') if response else None)

            results.append({
                "task_unit_id": item.id,
                "task_unit_status": item.get_task_unit_status_display(),
                "unit_index": item.unit_index,
                "request_data": request_data,
                "response_data": gpt_processor.get_content(response) if gpt_processor else None,
                "error_message": latest_response.error_message if latest_response else None,
                "processing_time": latest_response.processing_time if latest_response else None,
            })

        logger.log(logging.DEBUG, f"API: The user {request.user.email} requested the list of task results,"
                                  f"and it has been successfully returned.")
        return self.get_paginated_response(results)


@method_decorator(login_required, name='dispatch')
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
            task_unit = get_cache_or_database(
                model=TaskUnit,
                primary_key=task_unit_id,
                cache_key=task_unit_cache_key(task_unit_id),
                timeout=CACHE_TIMEOUT_TASK_UNIT,
            )

            status = task_unit.task_unit_status

            if status and status in [TaskUnitStatus.PENDING, TaskUnitStatus.IN_PROGRESS]:
                logger.log(logging.INFO, f"API: Task {task_unit_id}'s response is not found. cached.")
                return JsonResponse({"error": "Task response is not found. cached."}, status=HTTP_404_NOT_FOUND)

            if task_unit.latest_response is None:
                logger.log(logging.INFO, f"API: Task {task_unit_id}'s response is not found.")
                return JsonResponse({"error": "Task response is not found."}, status=HTTP_404_NOT_FOUND)

            task_unit_result = get_cache_or_database(
                model=TaskUnitResponse,
                primary_key=task_unit.latest_response.id,
                cache_key=task_unit_response_cache_key(task_unit.latest_response.id),
                timeout=CACHE_TIMEOUT_TASK_UNIT_RESPONSE,
            )

            status = task_unit_result.task_response_status

            response_data = {
                "batch_id": task_unit.batch_job_id,
                "task_unit_id": task_unit_id,
                "status": task_unit_result.get_task_response_status_display()
            }

            if status == TaskUnitStatus.COMPLETED:
                json_data = task_unit_result.response_data
                gpt_processor = get_gpt_processor(company=json_data.get('Company'))
                response_data["response_data"] = gpt_processor.get_content(json_data)

            return JsonResponse(response_data, status=self.status_code_map.get(status, HTTP_500_INTERNAL_SERVER_ERROR))

        except TaskUnit.DoesNotExist:
            return JsonResponse({"error": "Task unit not found"}, status=HTTP_404_NOT_FOUND)

        except TaskUnitResponse.DoesNotExist:
            return JsonResponse({"error": "Task response not found"}, status=HTTP_404_NOT_FOUND)


@method_decorator(login_required, name='dispatch')
class BatchJobRunView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, batch_id):
        """작업을 시작"""
        try:
            batch_job = get_cache_or_database(
                model=BatchJob,
                primary_key=batch_id,
                cache_key=batch_job_cache_key(batch_id),
                timeout=CACHE_TIMEOUT_BATCH_JOB,
            )

            serializer = BatchJobConfigSerializer(batch_job)
            if batch_job.batch_job_status in [BatchJobStatus.PENDING, BatchJobStatus.IN_PROGRESS]:
                return Response(serializer.data, status=HTTP_202_ACCEPTED)

            batch_job.set_status(BatchJobStatus.PENDING)
            batch_job.save()

            process_batch_job.apply_async(args=[batch_job.id])

            return Response(serializer.data, status=HTTP_202_ACCEPTED)
        except BatchJob.DoesNotExist:
            logger.log(logging.ERROR, f"API: BatchJob not found.")
            return Response(
                {"error": "BatchJob not found."},
                status=HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            logger.log(logging.ERROR, f"API: ValueError: {str(e)}")
            return Response(
                {"error": str(e)},
                status=HTTP_400_BAD_REQUEST
            )

    def get(self, request, batch_id):
        """작업 상태 점검"""
        try:
            batch_job = get_cache_or_database(
                model=BatchJob,
                primary_key=batch_id,
                cache_key=batch_job_cache_key(batch_id),
                timeout=CACHE_TIMEOUT_BATCH_JOB,
            )

            status = batch_job.get_batch_job_status_display()

            return Response(
                {"id": batch_id,
                 "batch_job_status": status},
                status=HTTP_200_OK
            )

        except BatchJob.DoesNotExist:
            logger.log(logging.ERROR, f"API: BatchJob not found.")
            return Response(
                {"error": "BatchJob not found."},
                status=HTTP_404_NOT_FOUND
            )
