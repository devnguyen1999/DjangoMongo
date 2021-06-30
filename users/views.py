from django.conf import settings
from django.middleware import csrf
import jwt
from users.utils import generate_access_token, generate_refresh_token
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework import exceptions, status
from users.models import RefreshToken, User
from users.serializers import RefreshTokenSerializer, UserChangePasswordSerializer, UserEditProfileSerializer, UserSerializer, UserLogInSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
def user_sign_up(request):
    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            user_serializer.validated_data['password'] = make_password(
                user_serializer.validated_data['password'])
            user_serializer.save()
            return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def user_log_in(request):
    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserLogInSerializer(data=user_data)
        if user_serializer.is_valid():
            try:
                user = User.objects.get(
                    email=user_serializer.validated_data['email'])
            except User.DoesNotExist:
                return exceptions.AuthenticationFailed('User not found.')
            # if user.password is make_password(user_serializer.validated_data['password']):
            access_token = generate_access_token(user)
            refresh_token = generate_refresh_token(user)
            response = JsonResponse(
                {'access_token': access_token, }, status=status.HTTP_200_OK)
            response.set_cookie(key='refreshtoken',
                                value=refresh_token, httponly=True)
            return response
            # else:
            #     return JsonResponse({
            #         'error_message': 'Password is incorrect.',
            #         'error_code': 400
            #     }, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
@csrf_protect
def user_refresh_token(request):
    if request.method == 'PUT':
        refresh_token = request.COOKIES['refreshtoken']
        if refresh_token is None:
            raise exceptions.AuthenticationFailed(
                'Authentication credentials were not provided.')
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed(
                'Expired refresh token, please login again.')

        user = User.objects.get(id=payload.get('user_id'))
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')

        access_token = generate_access_token(user)
        return JsonResponse({'access_token': access_token})


@api_view(['PUT'])
def user_change_password(request):
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        raise exceptions.AuthenticationFailed('User not found')

    if request.method == 'PUT':
        user_data = JSONParser().parse(request)
        user_serializer = UserChangePasswordSerializer(user, data=user_data)
        if user_serializer.is_valid():
            user_serializer.validated_data['password'] = make_password(
                user_serializer.validated_data['new_password'])
            user_serializer.save()
            return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def user_edit_profile(request):
    try:
        user = User.objects.get(pk=request.user.id)
    except User.DoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        user_data = JSONParser().parse(request)
        user_serializer = UserEditProfileSerializer(user, data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
