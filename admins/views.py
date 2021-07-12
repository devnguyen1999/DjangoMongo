import os
from django.conf import settings
import jwt
from users.utils import generate_access_token, generate_refresh_token, account_activation_token, reset_password_token
from django.http.response import HttpResponseRedirect, JsonResponse
from rest_framework import status
from users.models import RefreshToken, User
from users.serializers import UserChangePasswordSerializer, UserSerializer, UserLogInSerializer, UserResetPasswordSerializer, UserForgotPasswordSerializer
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def log_in(request):
    if request.method == 'POST':
        admin_data = request.data
        admin_serializer = UserLogInSerializer(data=admin_data)
        if admin_serializer.is_valid():
            try:
                admin = User.objects.get(
                    email=admin_serializer.validated_data['email'])
            except User.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'Admin not found.', },  status=status.HTTP_404_NOT_FOUND)
            if check_password(admin_serializer.validated_data['password'], admin.password):
                if ('Admin' in admin.roles):
                    access_token = generate_access_token(admin)
                    refresh_token = generate_refresh_token(admin)
                    token = RefreshToken(user=admin, token=refresh_token)
                    token.save()
                    response = JsonResponse(
                        {'access_token': access_token, }, status=status.HTTP_200_OK)
                    response.set_cookie(key='refreshtoken',
                                        value=refresh_token, httponly=True)
                    return response
                else:
                    return JsonResponse(
                    {'error_message': 'You are not an admin.', }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return JsonResponse(
                    {'error_message': 'Password is incorrect.', }, status=status.HTTP_401_UNAUTHORIZED)
        return JsonResponse(admin_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def refresh_token(request):
    if request.method == 'PUT':
        refresh_token = request.COOKIES['refreshtoken']
        if refresh_token is None:
            return JsonResponse(
                {'error_message': 'Authentication credentials were not provided.', },  status=status.HTTP_400_BAD_REQUEST)
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            try:
                rf_token = RefreshToken.objects.get(token=refresh_token)
            except RefreshToken.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'Refresh token not found.', },  status=status.HTTP_404_NOT_FOUND)
        try:
            admin = User.objects.get(id=payload.get('user_id'))
        except User.DoesNotExist:
            return JsonResponse(
                {'error_message': 'Admin not found.', },  status=status.HTTP_404_NOT_FOUND)
        access_token = generate_access_token(admin)
        if(jwt.ExpiredSignatureError):
            rf_token.token = generate_refresh_token(admin)
            rf_token.save()
            return JsonResponse(
                {'access_token': access_token, 'refresh_token': rf_token.token}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {'access_token': access_token, }, status=status.HTTP_200_OK)


@api_view(['PUT'])
def change_password(request):
    if request.method == 'PUT':
        try:
            admin = User.objects.get(pk=request.admin.id)
        except User.DoesNotExist:
            return JsonResponse(
                {'error_message': 'Admin not found.', },  status=status.HTTP_404_NOT_FOUND)
        admin_data = request.data
        admin_serializer = UserChangePasswordSerializer(admin, data=admin_data)
        if admin_serializer.is_valid():
            if check_password(admin_serializer.validated_data['password'], admin.password):
                admin_serializer.validated_data['password'] = make_password(
                    admin_serializer.validated_data['new_password'])
                admin_serializer.save()
                return JsonResponse(
                    {'message': 'Password has been changed.'}, status=status.HTTP_200_OK)
            else:
                return JsonResponse(
                    {'error_message': 'Password is incorrect.', }, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(admin_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    if request.method == 'POST':
        admin_data = request.data
        admin_serializer = UserForgotPasswordSerializer(data=admin_data)
        if admin_serializer.is_valid():
            try:
                admin = User.objects.get(
                    email=admin_serializer.validated_data['email'])
            except User.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'Admin not found.', },  status=status.HTTP_404_NOT_FOUND)
            try:
                uidb64 = urlsafe_base64_encode(force_bytes(admin.id))
                verify_account_token = reset_password_token.make_token(
                    admin)
                data = {
                    'first_name': admin.first_name,
                    'url': request.scheme + '://' + request.get_host() + '/api/admin/reset-password/' + uidb64 + '/' + verify_account_token,
                }
                message = get_template(os.path.join(
                    settings.BASE_DIR, 'users/templates/reset_password.html')).render(data)
                msg = EmailMessage(
                    'Reset your password.',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_serializer.validated_data['email']]
                )
                msg.content_subtype = "html"
                msg.send()
            except Exception:
                return JsonResponse(
                    {'error_message': 'An error occurred. Please try again.', },  status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(
                {'message': 'Email has been sent. Please check your inbox.', }, status=status.HTTP_200_OK)
        return JsonResponse(admin_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def reset_password(request):
    if request.method == 'PUT':
        data = request.data
        data_serializer = UserResetPasswordSerializer(data=data)
        if data_serializer.is_valid():
            try:
                id = urlsafe_base64_decode(
                    data_serializer.validated_data['uidb64'])
                admin = User.objects.get(id=id)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return JsonResponse(
                    {'error_message': 'An error occurred. Please try again.', },  status=status.HTTP_400_BAD_REQUEST)
            if reset_password_token.check_token(admin, data_serializer.validated_data['token']):
                admin_serializer = UserSerializer(
                    admin, data={'password': make_password(data_serializer.validated_data['new_password'])}, partial=True)
                if admin_serializer.is_valid():
                    admin_serializer.save()
                    return JsonResponse(
                        {'message': 'Password has been changed.', }, status=status.HTTP_200_OK)
                else:
                    return JsonResponse(
                        admin_serializer.errors,  status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(
            data_serializer.errors,  status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def edit_profile(request):
    try:
        admin = User.objects.get(pk=request.admin.id)
    except User.DoesNotExist:
        return JsonResponse(
            {'message': 'Admin not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        admin_data = request.data
        admin_serializer = UserSerializer(admin, data=admin_data)
        if admin_serializer.is_valid():
            admin_serializer.save()
            return JsonResponse(
                admin_serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(admin_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
