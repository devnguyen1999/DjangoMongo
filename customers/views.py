import os
from django.conf import settings
from django.utils.decorators import method_decorator
import jwt
from rest_framework.views import APIView
from users.utils import generate_access_token, generate_refresh_token, account_activation_token
from django.http.response import HttpResponseRedirect, JsonResponse
from rest_framework import status
from users.models import RefreshToken, User
from users.serializers import UserSerializer, UserLogInSerializer
from django.contrib.auth.hashers import check_password, make_password
from django.views.decorators.csrf import ensure_csrf_cookie
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

# Create your views here.


class SignUpView(APIView):

    def post(self, request, format=None):
        customer_serializer = UserSerializer(data=request.data)
        if customer_serializer.is_valid():
            customer_serializer.validated_data['password'] = make_password(
                customer_serializer.validated_data['password'])
            customer_serializer.save()
            try:
                customer = User.objects.get(
                    email=customer_serializer.validated_data['email'])
            except User.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'No user found to send confirmation email.', },  status=status.HTTP_404_NOT_FOUND)
            try:
                uidb64 = urlsafe_base64_encode(force_bytes(customer.id))
                verify_account_token = account_activation_token.make_token(
                    customer)
                data = {
                    'first_name': customer.first_name,
                    'url': request.scheme + '://' + request.get_host() + '/api/customer/verify-account/' + uidb64 + '/' + verify_account_token,
                }
                message = get_template(os.path.join(
                    settings.BASE_DIR, 'customers/templates/verify_account.html')).render(data)
                msg = EmailMessage(
                    'Verify your account.',
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [customer_serializer.validated_data['email']]
                )
                msg.content_subtype = "html"
                msg.send()
            except Exception:
                customer.delete()
                return JsonResponse(
                    {'error_message': 'An error occurred. Please try again.', },  status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(
                customer_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(customer_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class VerifyAccountView(APIView):

    def get(self, request, uidb64, token, format=None):
        try:
            id = urlsafe_base64_decode(uidb64)
            customer = User.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponseRedirect(redirect_to='https://www.google.com.vn/')
        if account_activation_token.check_token(customer, token):
            customer.is_verified = True
            customer.save()
            return HttpResponseRedirect(redirect_to='https://www.facebook.com/')


class LogInView(APIView):
    
    @method_decorator([ensure_csrf_cookie])
    def post(self, request, format=None):
        customer_serializer = UserLogInSerializer(data=request.data)
        if customer_serializer.is_valid():
            try:
                customer = User.objects.get(
                    email=customer_serializer.validated_data['email'])
            except User.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'User not found.', },  status=status.HTTP_404_NOT_FOUND)
            if check_password(customer_serializer.validated_data['password'], customer.password):
                access_token = generate_access_token(customer)
                refresh_token = generate_refresh_token(customer)
                token = RefreshToken(user=customer, token=refresh_token)
                token.save()
                response = JsonResponse(
                    {'access_token': access_token, }, status=status.HTTP_200_OK)
                response.set_cookie(key='refreshtoken',
                                    value=refresh_token, httponly=True)
                return response
            else:
                return JsonResponse(
                    {'error_message': 'Password is incorrect.', }, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(customer_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
