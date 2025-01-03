from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import UserRegistrationForm


@api_view(['POST'])
def register_user(request):
    form = UserRegistrationForm(data=request.data)
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        return Response({"message": "User registered successfully."}, status=201)
    return Response({"errors": form.errors}, status=400)
