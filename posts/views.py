from admins.decorators import admin_only
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from posts.serializers import PostSerializer
from django.http.response import JsonResponse
from rest_framework import exceptions, status
from posts.models import Post
from rest_framework.views import APIView
from django.utils.decorators import method_decorator

# Create your views here.


class CreatePostView(APIView):
    
    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def post(self, request, format=None):
        post_serializer = PostSerializer(data=request.data)
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse(post_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostView(APIView):

    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise exceptions.NotFound('Post not found.')

    def get(self, request, pk, format=None):
        post = self.get_object(pk)
        post_serializer = PostSerializer(post)
        return JsonResponse(post_serializer.data)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def patch(self, request, pk, format=None):
        post = self.get_object(pk)
        post_serializer = PostSerializer(post, data=request.data, partial=True)
        if post_serializer.is_valid():
            post_serializer.save()
            return JsonResponse(post_serializer.data)
        return JsonResponse(post_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @permission_classes([IsAuthenticated])
    @method_decorator([admin_only])
    def delete(self, request, pk, format=None):
        post = self.get_object(pk)
        post.delete()
        return JsonResponse({'message': 'Post was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

