from django.urls import path
from admins import views

urlpatterns = [
    path('log-in', views.log_in, name='log_in'),
]