import os, jwt
from django.conf import settings
from rest_framework.views import APIView
from users.utils import account_activation_token, generate_access_token, generate_refresh_token, reset_password_token
from django.http.response import HttpResponseRedirect, JsonResponse
from rest_framework import exceptions, status
from users.models import RefreshToken, User
from users.serializers import UserChangePasswordSerializer, UserLogInSerializer, UserSerializer, UserResetPasswordSerializer, UserForgotPasswordSerializer
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

# Create your views here.

class SignUpView(APIView):

    def post(self, request, format=None):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.validated_data['password'] = make_password(
                user_serializer.validated_data['password'])
            user_serializer.save()
            try:
                user = User.objects.get(
                    email=user_serializer.validated_data['email'])
            except User.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'No user found to send confirmation email.', },  status=status.HTTP_404_NOT_FOUND)
            try:
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                verify_account_token = account_activation_token.make_token(
                    user)
                data = {
                    'first_name': user.first_name,
                    'url': request.scheme + '://' + request.get_host() + '/api/user/verify-account/' + uidb64 + '/' + verify_account_token,
                }
                message = get_template(os.path.join(
                    settings.BASE_DIR, 'customers/templates/verify_account.html')).render(data)
                msg = EmailMessage(
                    'Verify your account.',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user_serializer.validated_data['email']]
                )
                msg.content_subtype = "html"
                msg.send()
            except Exception:
                user.delete()
                return JsonResponse(
                    {'error_message': 'An error occurred. Please try again.', },  status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(
                user_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(user_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class VerifyAccountView(APIView):

    def get(self, request, uidb64, token, format=None):
        try:
            id = urlsafe_base64_decode(uidb64)
            user = User.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponseRedirect(redirect_to='https://www.google.com.vn/')
        if account_activation_token.check_token(user, token):
            user.is_verified = True
            user.save()
            return HttpResponseRedirect(redirect_to='https://www.facebook.com/')


class LogInView(APIView):
    
    @method_decorator([ensure_csrf_cookie])
    def post(self, request, format=None):
        user_serializer = UserLogInSerializer(data=request.data)
        if user_serializer.is_valid():
            try:
                user = User.objects.get(
                    email=user_serializer.validated_data['email'])
            except User.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'User not found.', },  status=status.HTTP_404_NOT_FOUND)
            if check_password(user_serializer.validated_data['password'], user.password):
                access_token = generate_access_token(user)
                refresh_token = generate_refresh_token(user)
                token = RefreshToken(user=user, token=refresh_token)
                token.save()
                response = JsonResponse(
                    {'access_token': access_token, }, status=status.HTTP_200_OK)
                response.set_cookie(key='refreshtoken',
                                    value=refresh_token, httponly=True)
                return response
            else:
                return JsonResponse(
                    {'error_message': 'Password is incorrect.', }, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(user_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

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
