from products.models import Product
from products.pagination import CustomPagination
from categories.models import Category
from admins.decorators import admin_only
from rest_framework.decorators import parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from posts.serializers import DeleteImageSerializer, UploadImageSerializer, PostSerializer
from django.http.response import JsonResponse
from rest_framework import exceptions, status
from posts.models import Post
from users.models import User
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
import cloudinary.uploader
from django.core.serializers import serialize 
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.

class ProductsView(APIView):
    pagination_class = CustomPagination
    def get(self, request, format=None):
        product = Product.objects.all()        
        product_serializer = PostSerializer(product, many=True)
        return JsonResponse(product_serializer.data, safe=False)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    @parser_classes([MultiPartParser, FormParser])
    def post(self, request, format=None):
        product_serializer = PostSerializer(data=request.data)
        if product_serializer.is_valid():
            try:
                user = User.objects.get(pk=request.user.id)
            except User.DoesNotExist:
                raise exceptions.NotFound('Admin not found.')
            product_serializer.validated_data['created_by'] = user
            try:
                category = Category.objects.get(pk=product_serializer.validated_data['category'])
            except Category.DoesNotExist:
                raise exceptions.NotFound('Category not found.')
            product_serializer.validated_data['category'] = category
            upload_data = cloudinary.uploader.upload(
                product_serializer.validated_data['images'], folder='djangomongo/products')
            product_serializer.validated_data['images'][0] = upload_data['secure_url']
            product_serializer.save()
            return JsonResponse({'success': True}, status=status.HTTP_201_CREATED, safe=False)
        return JsonResponse(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductView(APIView):

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise exceptions.NotFound('Product not found.')

    def get(self, request, pk, format=None):
        product = self.get_object(pk)
        product_serializer = PostSerializer(product)
        return JsonResponse(product_serializer.data)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def patch(self, request, pk, format=None):
        product = self.get_object(pk)
        product_serializer = PostSerializer(product, data=request.data, partial=True)
        if product_serializer.is_valid():
            product_serializer.save()
            return JsonResponse({'success': True})
        return JsonResponse(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def delete(self, request, pk, format=None):
        product = self.get_object(pk)
        product.delete()
        return JsonResponse({'message': 'Post was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

