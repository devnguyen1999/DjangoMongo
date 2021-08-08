from categories.models import Category
from categories.serializers import CategorySerializer
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


class CategoriesView(APIView):

    def get(self, request, format=None):
        categories = Category.objects.all()        
        categories_serializer = CategorySerializer(categories, many=True)
        return JsonResponse(categories_serializer.data, safe=False)
    
    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def post(self, request, format=None):
        category_serializer = CategorySerializer(data=request.data)
        if category_serializer.is_valid():
            category_serializer.save()
            return JsonResponse({'success': True}, status=status.HTTP_201_CREATED)
        return JsonResponse(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CategoryView(APIView):

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise exceptions.NotFound('Category not found.')

    def get(self, request, pk, format=None):
        category = self.get_object(pk)
        category_serializer = CategorySerializer(category)
        return JsonResponse(category_serializer.data)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def patch(self, request, pk, format=None):
        category = self.get_object(pk)
        category_serializer = CategorySerializer(category, data=request.data, partial=True)
        if category_serializer.is_valid():
            category_serializer.save()
            return JsonResponse({'success': True}, status=status.HTTP_200_OK)
        return JsonResponse(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def delete(self, request, pk, format=None):
        category = self.get_object(pk)
        category.delete()
        return JsonResponse({'message': 'Category was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
