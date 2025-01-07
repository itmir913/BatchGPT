import logging

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer


class RegisterView(APIView):
    def post(self, request):
        """
        회원가입 기능
        :param request:
        :return:
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            logger = logging.getLogger(__name__)
            logger.warning(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def check_authentication(request):
    """
    현재 사용자가 로그인되어 있는지 확인하는 기능
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        return JsonResponse(
            {'is_authenticated': True,
             'email': request.user.email,
             'balance': request.user.balance
             })
    else:
        return JsonResponse({'is_authenticated': False})


@api_view(['POST'])
def login_view(request):
    """
    로그인 기능
    :param request:
    :return:
    """
    email = request.data.get('email')
    password = request.data.get('password')

    # 사용자 인증
    user = authenticate(request, username=email, password=password)

    if user is not None:
        # 인증 성공
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': user.username,
            'balance': user.balance,
        }, status=status.HTTP_200_OK)
    else:
        # 인증 실패
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


def logout_view(request):
    """
    로그아웃 기능
    :param request:
    :return:
    """
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'Logged out successfully.'}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)
