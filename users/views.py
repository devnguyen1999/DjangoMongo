import os, jwt
from django.conf import settings
from rest_framework.views import APIView
from users.utils import generate_access_token, generate_refresh_token, reset_password_token
from django.http.response import JsonResponse
from rest_framework import exceptions, status
from users.models import RefreshToken, User
from users.serializers import UserChangePasswordSerializer, UserSerializer, UserResetPasswordSerializer, UserForgotPasswordSerializer
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

# Create your views here.

class RefreshTokenView(APIView):

    def patch(self, request, format=None):
        refresh_token = request.COOKIES['refreshtoken']
        if refresh_token is None:
            return JsonResponse(
                {'error_message': 'Authentication credentials were not provided.', },  status=status.HTTP_400_BAD_REQUEST)
        is_expired = False
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            is_expired = True
        try:
            user = User.objects.get(id=payload.get('user_id'))
        except User.DoesNotExist:
            return JsonResponse(
                {'error_message': 'User not found.', },  status=status.HTTP_404_NOT_FOUND)
        access_token = generate_access_token(user)
        if is_expired:
            try:
                rf_token = RefreshToken.objects.get(token=refresh_token)
            except RefreshToken.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'Refresh token not found.', },  status=status.HTTP_404_NOT_FOUND)
            rf_token.token = generate_refresh_token(user)
            rf_token.save()
            return JsonResponse(
                {'access_token': access_token, 'refresh_token': rf_token.token})
        else:
            return JsonResponse(
                {'access_token': access_token, })

class ChangePasswordView(APIView):

    @permission_classes([IsAuthenticated])
    def patch(self, request, format=None):
        try:
            user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            return JsonResponse(
                {'error_message': 'User not found.', },  status=status.HTTP_404_NOT_FOUND)
        user_data = request.data
        user_serializer = UserChangePasswordSerializer(user, data=user_data)
        if user_serializer.is_valid():
            if check_password(user_serializer.validated_data['password'], user.password):
                user_serializer.validated_data['password'] = make_password(
                    user_serializer.validated_data['new_password'])
                user_serializer.save()
                return JsonResponse(
                    {'message': 'Password has been changed.'})
            else:
                return JsonResponse(
                    {'error_message': 'Password is incorrect.', }, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(user_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):

    def get_object(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.NotFound('User not found.')

    def post(self, request, format=None):
        user_serializer = UserForgotPasswordSerializer(data=request.data)
        if user_serializer.is_valid():
            user = self.get_object(user_serializer.validated_data['email'])
            try:
                uidb64 = urlsafe_base64_encode(force_bytes(user.email))
                verify_account_token = reset_password_token.make_token(user)
                data = {
                    'first_name': user.first_name,
                    'url': request.scheme + '://' + request.get_host() + '/api/user/reset-password/' + uidb64 + '/' + verify_account_token,
                }
                message = get_template(os.path.join(
                    settings.BASE_DIR, 'users/templates/reset_password.html')).render(data)
                msg = EmailMessage(
                    'Reset your password.',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user_serializer.validated_data['email']]
                )
                msg.content_subtype = "html"
                msg.send()
            except Exception:
                return JsonResponse(
                    {'error_message': 'An error occurred. Please try again.', },  status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(
                {'message': 'Email has been sent. Please check your inbox.', })
        return JsonResponse(user_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, format=None):
        data_serializer = UserResetPasswordSerializer(data=request.data)
        if data_serializer.is_valid():
            email = urlsafe_base64_decode(
                data_serializer.validated_data['uidb64'])
            user = self.get_object(email)
            if reset_password_token.check_token(user, data_serializer.validated_data['token']):
                user_serializer = UserSerializer(
                    user, data={'password': make_password(data_serializer.validated_data['new_password'])}, partial=True)
                if user_serializer.is_valid():
                    user_serializer.save()
                    return JsonResponse(
                        {'message': 'Password has been changed.', })
                else:
                    return JsonResponse(
                        user_serializer.errors,  status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(
            data_serializer.errors,  status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise exceptions.NotFound('User not found.')

    @permission_classes([IsAuthenticated])
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        user_serializer = UserSerializer(user)
        return JsonResponse(user_serializer.data)

    @permission_classes([IsAuthenticated])
    def patch(self, request, pk, format=None):
        user = self.get_object(pk)
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse(user_serializer.data)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
