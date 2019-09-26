# 
#  Copyright 2019 Altran. All rights reserved.
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# 
# 
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
