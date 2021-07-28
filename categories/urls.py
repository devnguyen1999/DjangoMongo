from categories.views import CategoryView, CreateCategoryView
from django.urls import path

urlpatterns = [
    path('create', CreateCategoryView.as_view(), name='create_category'),
    path('detail/<int:pk>', CategoryView.as_view(), name='category_detail'),
]