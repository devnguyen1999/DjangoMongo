from users.models import User


def check_customer_by_id(id):
    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        return False
    if ('Customer' in user.roles):
        return user
    else:
        return False

def check_customer_by_email(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False
    if ('Customer' in user.roles):
        return user
    else:
        return False