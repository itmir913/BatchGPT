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
        logger = logging.getLogger(__name__)

        if serializer.is_valid():
            serializer.save()
            logger.log(logging.DEBUG, f"API: User registered successfully.")
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        else:
            logger.log(logging.ERROR, f"API: User registration failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def check_authentication(request):
    """
    현재 사용자가 로그인되어 있는지 확인하는 기능
    :param request:
    :return:
    """
    logger = logging.getLogger(__name__)

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
    logger = logging.getLogger(__name__)

    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(request, username=email, password=password)

    if user is not None:
        logger.log(logging.DEBUG, f"API: {email} has logged in.")
        login(request, user)
        return Response({
            'message': 'Login successful',
            'user': user.username,
            'balance': user.balance,
        }, status=status.HTTP_200_OK)
    else:
        logger.log(logging.DEBUG, f"API: An attempt to log in with {email} was made, but authentication failed.")
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


def logout_view(request):
    """
    로그아웃 기능
    :param request:
    :return:
    """
    logger = logging.getLogger(__name__)

    if request.method == 'POST':
        logger.log(logging.DEBUG, f"API: {request.user.email} has logged out.")
        logout(request)
        return JsonResponse({'message': 'Logged out successfully.'}, status=200)

    logger.log(logging.ERROR, f"API: The logout for {request.user} has failed.")
    return JsonResponse({'error': 'Invalid request method.'}, status=400)
