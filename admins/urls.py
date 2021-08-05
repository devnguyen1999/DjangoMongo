from django.urls import path
from admins.views import LoginView

urlpatterns = [
    path('/log-in', LoginView.as_view(), name='log_in'),
]