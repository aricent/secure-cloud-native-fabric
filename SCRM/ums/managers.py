"""
User model Custom manager
"""
from django.contrib.auth.models import BaseUserManager


class ScfUserManager(BaseUserManager):
    """
    overrides BaseUserManager class for
    default django random password and normalize_email functionality
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Email is needed')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        """ create normal user"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('username', email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('username', email)
        return self._create_user(email, password, **extra_fields)

    def create_staff(self, email, password, **extra_fields):
        """ create staff user"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('username', email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('username', email)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """ create admin user"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('username', email)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)
