from django.urls import path
from customers import views

urlpatterns = [
    path('sign-up', views.sign_up, name='sign_up'),
    path('verify-account/<uidb64>/<token>', views.verify_account, name='verify_account'),
    path('log-in', views.log_in, name='log_in'),
]