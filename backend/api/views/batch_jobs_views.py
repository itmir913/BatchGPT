from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.views import APIView

from api.serializers.BatchJobSerializer import BatchJobSerializer, BatchJobCreateSerializer
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

    def get(self, request, id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=id)

        # 현재 요청한 사용자가 소유자인지 확인
        if batch_job.user != request.user:
            return Response(
                {"error": "You do not have permission to access this resource."},
                status=HTTP_403_FORBIDDEN,
            )

        # 직렬화하여 응답 반환
        serializer = BatchJobSerializer(batch_job)
        return Response(serializer.data, status=HTTP_200_OK)


class BatchJobFileUploadView(APIView):
    """
    API 엔드포인트: 특정 BatchJob에 파일 업로드
    - URL: /api/batch-jobs/{id}/upload/
    - 메서드: PATCH
    """
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def patch(self, request, id):
        # ID로 BatchJob 객체 가져오기 (404 처리 포함)
        batch_job = get_object_or_404(BatchJob, id=id)

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

            batch_job.file = file
            batch_job.save()
        except ValidationError as e:
            return Response(
                {"error": e.message},
                status=HTTP_400_BAD_REQUEST,
            )

        # 응답 데이터 직렬화 및 반환
        return Response(
            {
                "id": batch_job.id,
                "title": batch_job.title,
                "description": batch_job.description,
                "file": batch_job.file.url if batch_job.file else None,
                "file_type": batch_job.file_type,
                "created_at": batch_job.created_at,
                "updated_at": batch_job.updated_at,
            },
            status=HTTP_200_OK,
        )
