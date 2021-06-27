from django.urls import path
from django.urls.conf import include

from users import views

urlpatterns = [
    path('sign-up', views.user_sign_up, name='sign_up'),
    path('log-in', views.user_log_in, name='log_in'),
    path('change-password', views.user_change_password, name='change_password'),
    path('edit-profile', views.user_edit_profile, name='edit_profile'),
]