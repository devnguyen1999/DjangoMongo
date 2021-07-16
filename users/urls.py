from django.urls import path
from users.views import RefreshTokenView, ChangePasswordView, ForgotPasswordView, UserProfileView

urlpatterns = [
    path('refresh-token', RefreshTokenView.as_view(), name='refresh_token'),
    path('change-password', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('profile', UserProfileView.as_view(), name='profile'),
]