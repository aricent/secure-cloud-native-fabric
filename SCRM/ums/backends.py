"""
Email Auth backend
By default django support username authentication
In SCF we need email authentication
"""
from django.contrib.auth.backends import ModelBackend

from .models import ScfUser


class EmailBackend(ModelBackend):
    """ Custom Email backend class"""
    def authenticate(self, email=None, password=None, **kwargs):
        """ created custom authentication method """
        try:
            user = ScfUser.objects.get(email=email)
        except ScfUser.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
