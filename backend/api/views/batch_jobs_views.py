from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from api.serializers.BatchJobSerializer import BatchJobSerializer
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
        batch_jobs = BatchJob.objects.filter(user=request.user)
        serializer = BatchJobSerializer(batch_jobs, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    # def post(self, request):
    #     """
    #     Create a new batch job for the authenticated user.
    #     """
    #     # 요청 데이터에 현재 사용자를 추가하여 새로운 BatchJob 생성
    #     data = request.data.copy()
    #     data['user'] = request.user.id  # 사용자 ID를 데이터에 포함
    #     serializer = BatchJobSerializer(data=data)
    #
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
