""" User and users uri"""

from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView

from .views import (UserViewSet,
                    Login,
                    Logout,
                    Signup)

router = DefaultRouter()

router.register(r'users', UserViewSet)

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'user/login/$', Login.as_view(), name="scf-login"),
    url(r'user/logout/$', Logout.as_view(), name="scf-logout"),
    url(r'user/signup/$', Signup.as_view(), name="scf-signup"),
    url(r'signup/$', TemplateView.as_view(template_name="../templates/signup.html")),
]
