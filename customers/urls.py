from django.urls import path
from customers import views

urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('verify-account/<uidb64>/<token>', views.verify_account, name='verify_account'),
    path('log-in', views.log_in, name='log_in'),
    path('refresh-token', views.refresh_token, name='refresh_token'),
    path('change-password', views.change_password, name='change_password'),
    path('forgot-password', views.forgot_password, name='forgot_password'),
    path('reset-password', views.reset_password, name='reset_password'),
    path('edit-profile', views.edit_profile, name='edit_profile'),
]