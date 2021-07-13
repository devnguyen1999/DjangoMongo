import os
from django.conf import settings
import jwt
from users.utils import generate_access_token, generate_refresh_token, account_activation_token
from django.http.response import HttpResponseRedirect, JsonResponse
from rest_framework import status
from users.models import RefreshToken, User
from users.serializers import UserSerializer, UserLogInSerializer
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
def sign_up(request):
    if request.method == 'POST':
        customer_data = request.data
        customer_serializer = UserSerializer(data=customer_data)
        if customer_serializer.is_valid():
            customer_serializer.validated_data['password'] = make_password(
                customer_serializer.validated_data['password'])
            customer_serializer.save()
            try:
                customer = User.objects.get(
                    email=customer_serializer.validated_data['email'])
            except User.DoesNotExist:
                return JsonResponse(
                    {'error_message': 'User not found.', },  status=status.HTTP_404_NOT_FOUND)
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


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_account(request, uidb64, token):
    if request.method == 'GET':
        try:
            id = urlsafe_base64_decode(uidb64)
            customer = User.objects.get(id=id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponseRedirect(redirect_to='https://www.google.com.vn/')
        if account_activation_token.check_token(customer, token):
            customer.is_verified = True
            customer.save()
            return HttpResponseRedirect(redirect_to='https://www.facebook.com/')


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def log_in(request):
    if request.method == 'POST':
        customer_data = request.data
        customer_serializer = UserLogInSerializer(data=customer_data)
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
                token = RefreshToken(customer=customer, token=refresh_token)
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

