from admins.authentication import check_admin_by_email
from users.utils import generate_access_token, generate_refresh_token
from django.http.response import JsonResponse
from rest_framework import status
from users.models import RefreshToken
from users.serializers import UserLogInSerializer
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.


@api_view(['POST'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def log_in(request):
    if request.method == 'POST':
        admin_data = request.data
        admin_serializer = UserLogInSerializer(data=admin_data)
        if admin_serializer.is_valid():
            admin = check_admin_by_email(
                admin_serializer.validated_data['email'])
            if admin is not False:
                if check_password(admin_serializer.validated_data['password'], admin.password):
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
                        {'error_message': 'Password is incorrect.', }, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return JsonResponse(
                    {'error_message': 'Admin not found.', },  status=status.HTTP_404_NOT_FOUND)
        return JsonResponse(admin_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

