# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from rest_framework.authtoken.models import Token

from .managers import ScfUserManager


class ScfUser(AbstractBaseUser, PermissionsMixin):
    """
    We have overrides default Django user
    PermissionsMixin classes we have used for
    using extra authentication feature like is_admin etc..
    """

    class Meta:
        """ Proxy false means create new model"""
        verbose_name = 'ScfUser'
        db_table = 'scf_user'
        proxy = False

    email = models.EmailField(max_length=128, unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=50, null=True, verbose_name='First Name')
    last_name = models.CharField(max_length=128, null=True, verbose_name='Last Name')
    is_staff = models.BooleanField(default=False, verbose_name='Is Staff')
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='Date of Register')
    is_active = models.BooleanField(default=False, verbose_name='Active')

    username = models.CharField(max_length=128, unique=True, default='')

    objects = ScfUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def user_is_superuser(self):
        """ Custom user_is_superuser check method"""
        return self.is_superuser

    def get_full_name(self):
        """ Custom full_name"""
        inactive = '(inactive)' if not self.is_active else ''
        full_name = u'{first} {last} {status}'. \
            format(first=self.first_name, last=self.last_name, status=inactive)
        return full_name.strip()

    @property
    def full_name(self):
        """ implements abstract method"""
        return self.get_full_name()

    def get_short_name(self):
        """ short name"""
        return self.email

    def get_session_token(self):
        """ get token from User instance """
        return Token.objects.get_or_create(user=self)[0].key
