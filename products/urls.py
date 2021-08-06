from posts.views import PostView, PostsView
from django.urls import path

urlpatterns = [
    path('', PostsView.as_view(), name='posts'),
    path('detail/<int:pk>', PostView.as_view(), name='post_detail'),
]