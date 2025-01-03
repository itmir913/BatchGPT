from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import UserRegistrationForm


def check_authentication(request):
    if request.user.is_authenticated:
        return JsonResponse({'is_authenticated': True})
    else:
        return JsonResponse({'is_authenticated': False})


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    # 사용자 인증
    user = authenticate(request, username=email, password=password)

    if user is not None:
        # 인증 성공
        return Response({'message': 'Login successful', 'user': user.username}, status=status.HTTP_200_OK)
    else:
        # 인증 실패
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def register_user(request):
    form = UserRegistrationForm(data=request.data)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return Response({"message": "User registered successfully."}, status=201)
    return Response({"errors": form.errors}, status=400)
