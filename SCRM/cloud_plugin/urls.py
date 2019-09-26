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
'''
from rest_framework.urlpatterns import format_suffix_patterns
from .views import RegionViewSet, SecurityGroupViewSet, VpcViewSet
from django.conf.urls import url

securitygroup_list = SecurityGroupViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
securitygroup_detail = SecurityGroupViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})
region_list = RegionViewSet.as_view({
    'get': 'list'
})
region_detail = RegionViewSet.as_view({
    'get': 'retrieve'
})
vpc_list = VpcViewSet.as_view({
    'get': 'list'
})
vpc_detail = VpcViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = format_suffix_patterns([
    url(r'^securitygroup/$', securitygroup_list, name='securitygroup-list'),
    url(r'^securitygroup/(?P<pk>[A-Za-z0-9-]+)/$', securitygroup_detail, name='securitygroup-detail'),
    url(r'^region/$', region_list, name='region-list'),
    url(r'^region/(?P<pk>[A-Za-z0-9-]+)/$', region_detail, name='region-detail'),
    url(r'^vpc/$', vpc_list, name='vpc-list'),
    url(r'^vpc_detail/(?P<pk>[A-Za-z0-9-]+)/$', vpc_detail, name='vpc-detail')
])



'''
from django.conf.urls import url
from .views import  MonitoredObject, Policies,VpcList, CrispPostureGraph, CrispPostureMap, Auditor, RunAuditor, PolicyTemplate, PolicyInstances, Clouds
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^index/$', views.index, name='index'),
    url(r'^secgrp/$', views.secgrp, name='secgrp'),
    #url(r'^region/$', RegionList.as_view()),
    url(r'^vpc/$', VpcList.as_view()),
    #url(r'^vpc/region/(?P<pk>[A-Za-z0-9-]+)/$', OnlyVpcList.as_view()),
    #url(r'^vpc/(?P<pk>[A-Za-z0-9-]+)/$', VpcDetail.as_view()),
    #url(r'^securitygroup/$', SecurityGroupList.as_view()),
    #url(r'^securitygroup/(?P<pk>[A-Za-z0-9-]+)/$', SecurityGroupDetail.as_view()),
    #url(r'^securitygroup/(?P<pk>[A-Za-z0-9-]+)/ingress/$', SecurityGroupIngressDetail.as_view()),
    #url(r'^securitygroup/(?P<pk>[A-Za-z0-9-]+)/egress/$', SecurityGroupEgressDetail.as_view()),
    #url(r'^securitymonkey/$', SmIssueList.as_view()),
    #url(r'^alarms/$',Alarms.as_view()),
    url(r'^monitoredobject/$',MonitoredObject.as_view()),
    url(r'^policies/$',Policies.as_view()),
    url(r'^policypostures/$',CrispPostureGraph.as_view()),
    url(r'^policyposturemaps/$',CrispPostureMap.as_view()),
    url(r'^auditors/$',Auditor.as_view()),
    url(r'^runauditor/$',RunAuditor.as_view()),
    url(r'^policytemplates/$',PolicyTemplate.as_view()),
    url(r'^policyinstances/$',PolicyInstances.as_view()),
    url(r'^clouds/$',Clouds.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)


