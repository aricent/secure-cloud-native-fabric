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
"""SCRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


#from rest_framework.routers import DefaultRouter
#from cloud_plugin import views

# Create a router and register our viewsets with it.
#router = DefaultRouter()
#router.register(r'securitygroup', views.SecurityGroupViewSet)
#router.register(r'region', views.RegionViewSet)
#router.register(r'vpc', views.VpcViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
#urlpatterns = [
#    url(r'^', include(router.urls)),
#    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
#]

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', TemplateView.as_view(template_name='login.html'), name='login'),
    url(r'^', include('cloud_plugin.urls')),
    url(r'^', include('ums.urls')),
    url(r'^docs/', include_docs_urls(title='SCF')),
    url(r'^fw/$', TemplateView.as_view(template_name='firewall.html'), name='firewall'),
    url(r'^fw_details/$', TemplateView.as_view(template_name='fw_details.html'), name='firewall_details'),
    url(r'^comp_pub/$', TemplateView.as_view(template_name='compliancepub.html'), name='compliance_pub'),
    url(r'^comp/$', TemplateView.as_view(template_name='compliance.html'), name='compliance'),
    url(r'^comp_details/$', TemplateView.as_view(template_name='compliance_details.html'), name='compliance_details'),
    url(r'^comp_details_pub/$', TemplateView.as_view(template_name='compliance_detailspub.html'), name='compliance_details_pub'),
    url(r'^arch/$', TemplateView.as_view(template_name='architecture.html'), name='architecture'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
