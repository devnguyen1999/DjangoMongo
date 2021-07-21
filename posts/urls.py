from django.urls import path
from posts.views import CreatePostView, ImageView, PostView

urlpatterns = [
    path('create', CreatePostView.as_view(), name='create_post'),
    path('detail/<int:pk>', PostView.as_view(), name='post_detail'),
    path('image', ImageView.as_view(), name='image'),
]