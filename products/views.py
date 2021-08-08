from products.models import Product
from products.pagination import CustomPagination
from categories.models import Category
from admins.decorators import admin_only
from rest_framework.decorators import parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from products.serializers import ProductSerializer
from django.http.response import JsonResponse
from rest_framework import exceptions, status
from users.models import User
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser
import cloudinary.uploader

# Create your views here.


class ProductsView(APIView):
    pagination_class = CustomPagination

    def get(self, request, format=None):
        product = Product.objects.all()
        product_serializer = ProductSerializer(product, many=True)
        return JsonResponse(product_serializer.data, safe=False)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    @parser_classes([MultiPartParser, FormParser])
    def post(self, request, format=None):
        product_serializer = ProductSerializer(data=request.data)
        if product_serializer.is_valid():
            try:
                user = User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                raise exceptions.NotFound('Admin not found.')
            product_serializer.validated_data['created_by'] = user
            upload_data = cloudinary.uploader.upload(product_serializer.validated_data['images'], folder='djangomongo/products')
            product_serializer.validated_data['images'] = []
            product_serializer.validated_data['images'].append(upload_data['secure_url'])
            product_serializer.save()
            return JsonResponse({'success': True}, status=status.HTTP_201_CREATED)
        return JsonResponse(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductView(APIView):

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise exceptions.NotFound('Product not found.')

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        product_serializer = ProductSerializer(product)
        return JsonResponse(product_serializer.data)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        product_serializer = ProductSerializer(
            product, data=request.data, partial=True)
        if product_serializer.is_valid():
            product_serializer.save()
            return JsonResponse({'success': True})
        return JsonResponse(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return JsonResponse({'message': 'Product was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
