from django.urls import path
from customers.views import SignUpView, VerifyAccountView, LogInView

urlpatterns = [
    path('sign-up', SignUpView.as_view(), name='sign_up'),
    path('verify-account/<uidb64>/<token>', VerifyAccountView.as_view(), name='verify_account'),
    path('log-in', LogInView.as_view(), name='log_in'),
]