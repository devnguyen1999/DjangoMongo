from django.urls import path
from moderators.views import AddAdminView, RemoveAdminView

urlpatterns = [
    path('add-admin', AddAdminView.as_view(), name='add_admin'),
    path('remove-admin', RemoveAdminView.as_view(), name='remove_admin'),
]