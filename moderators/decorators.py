from django.core.exceptions import PermissionDenied
from rest_framework import exceptions
from users.models import User


def moderator_only(function):
    def wrap(request, *args, **kwargs):
        try:
            user = User.objects.get(pk=request.user.id)
        except User.DoesNotExist:
            raise exceptions.NotAuthenticated('Can not find moderator from access token.')
        if 'Moderator' in user.roles:
            return function(request, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied('Permission denied.')
    return wrap
