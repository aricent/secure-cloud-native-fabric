""" Registering myuser model in django admin panel"""

from django.contrib import admin


from .models import ScfUser

admin.site.register(ScfUser)
