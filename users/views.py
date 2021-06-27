from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import status
from users.models import User
from users.serializers import UserSignUpSerializer, UserLogInSerializer
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken as Refresh

# Create your views here.


@api_view(['POST'])
def user_sign_up(request):
    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserSignUpSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.validated_data['password'] = make_password(user_serializer.validated_data['password'])
            user_serializer.save()
            return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_log_in(request):
    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserLogInSerializer(data=user_data)
        if user_serializer.is_valid():
            user = authenticate(
                request,
                username=user_serializer.validated_data['email'],
                password=user_serializer.validated_data['password']
            )
            if user:
                refresh = Refresh.for_user(user)
                data = {
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token)
                }
                return JsonResponse(data, status=status.HTTP_200_OK)

            return JsonResponse({
                'error_message': 'email or password is incorrect.',
                'error_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
