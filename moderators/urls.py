from django.urls import path
from moderators import views

urlpatterns = [
    path('add-admin', views.add_admin, name='add_admin'),
    path('remove-admin', views.remove_admin, name='remove_admin'),
]