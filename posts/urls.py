from django.urls import path
from posts.views import ImageView, PostView, PostsView

urlpatterns = [
    path('', PostsView.as_view(), name='posts'),
    path('detail/<int:pk>', PostView.as_view(), name='post_detail'),
    path('image', ImageView.as_view(), name='image'),
]