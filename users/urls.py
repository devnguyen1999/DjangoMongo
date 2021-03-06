from django.urls import path
from users.views import LogInView, LogOutView, RefreshTokenView, ChangePasswordView, ForgotPasswordView, SignUpView, UserProfileView, VerifyAccountView

urlpatterns = [
    path('sign-up', SignUpView.as_view(), name='sign_up'),
    path('verify-email/<uidb64>/<token>', VerifyAccountView.as_view(), name='verify_email'),
    path('log-in', LogInView.as_view(), name='log_in'),
    path('log-out', LogOutView.as_view(), name='log_out'),
    path('refresh-token', RefreshTokenView.as_view(), name='refresh_token'),
    path('change-password', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password', ForgotPasswordView.as_view(), name='forgot_password'),
    path('profile', UserProfileView.as_view(), name='profile'),
]