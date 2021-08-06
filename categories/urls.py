from categories.views import CategoriesView, CategoryView
from django.urls import path

urlpatterns = [
    path('', CategoriesView.as_view(), name='categories'),
    path('detail/<int:pk>', CategoryView.as_view(), name='category_detail'),
]