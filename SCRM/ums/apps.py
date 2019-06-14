"""
Django created apps module
in this module we can add tasks in init
"""
from django.apps import AppConfig


class UmsappConfig(AppConfig):
    """ we can also register
    ums with UmsappConfig class
    """
    name = 'ums'
