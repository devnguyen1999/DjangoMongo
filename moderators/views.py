from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from moderators.decorators import moderator_only
from rest_framework import status
from users.serializers import UserSerializer
from users.models import User
from django.http.response import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework import exceptions

# Create your views here.

class AddAdminView(APIView):

    @permission_classes([IsAuthenticated])
    @method_decorator([moderator_only])
    def patch(self, request, format=None):
        try:
            admin = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            return JsonResponse(
                {'error_message': 'Admin not found.', },  status=status.HTTP_404_NOT_FOUND)
        admin = User.objects.get(email=request.data['email'])
        if 'Admin' not in admin.roles:
            roles = admin.roles.append('Admin')
            admin_serializer = UserSerializer(
                admin, data={'roles': roles}, partial=True)
            if admin_serializer.is_valid():
                admin_serializer.save()
                return JsonResponse(
                    admin_serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(admin_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(
            {'error_message': 'This person is already an administrator.', },  status=status.HTTP_400_BAD_REQUEST)


class RemoveAdminView(APIView):
    
    @permission_classes([IsAuthenticated])
    @method_decorator([moderator_only])
    def patch(self, request, format=None):
        try:
            customer = User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            return JsonResponse(
                {'error_message': 'Customer not found.', },  status=status.HTTP_404_NOT_FOUND)
        customer = User.objects.get(email=request.data['email'])
        if 'Admin' in customer.roles:
            roles = customer.roles.remove('Admin')
            customer_serializer = UserSerializer(
                customer, data={'roles': roles}, partial=True)
            if customer_serializer.is_valid():
                customer_serializer.save()
                return JsonResponse(
                    customer_serializer.data, status=status.HTTP_200_OK)
            return JsonResponse(customer_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(
            {'error_message': 'This person is not yet an administrator.', },  status=status.HTTP_400_BAD_REQUEST)

