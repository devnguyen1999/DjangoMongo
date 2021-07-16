from rest_framework import exceptions
from users.models import User


def admin_only(function):
    def wrap(request, *args, **kwargs):
        try:
            user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            raise exceptions.NotAuthenticated('Can not find admin from access token.')
        if 'Admin' in user.roles:
            return function(request, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied('Permission denied.')
    return wrap
