from django.urls import path
from users import views

urlpatterns = [
    path('sign-up', views.user_sign_up, name='sign_up'),
    path('log-in', views.user_log_in, name='log_in'),
    path('refresh-token', views.user_refresh_token, name='refresh_token'),
    path('change-password', views.user_change_password, name='change_password'),
    path('edit-profile', views.user_edit_profile, name='edit_profile'),
]