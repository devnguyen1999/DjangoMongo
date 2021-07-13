from django.urls import path
from users import views

urlpatterns = [
    path('refresh-token', views.refresh_token, name='refresh_token'),
    path('change-password', views.change_password, name='change_password'),
    path('forgot-password', views.forgot_password, name='forgot_password'),
    path('reset-password', views.reset_password, name='reset_password'),
    path('edit-profile', views.edit_profile, name='edit_profile'),
]