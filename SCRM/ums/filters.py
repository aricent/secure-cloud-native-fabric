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
"""
User filters
"""
from rest_framework.exceptions import ParseError
from django_filters import rest_framework as filters
from .models import ScfUser


class UserFilter(filters.FilterSet):
    """ user related filters"""

    class Help(object):
        """ created help text class"""

        def field_filter(field):
            """filter return by fields"""
            return u"Filters results by {}.".format(field)

        email = field_filter('email')
        first_name = field_filter('first name')
        last_name = field_filter('last name')
        name = field_filter('full name')
        status = field_filter('status') + " Values can be all, inactive, or active. " \
                                          "Active users are returned by default."

    email = filters.CharFilter(lookup_expr='icontains', help_text=Help.email)
    first_name = filters.CharFilter(lookup_expr='icontains', help_text=Help.first_name)
    last_name = filters.CharFilter(lookup_expr='icontains', help_text=Help.last_name)
    name = filters.CharFilter(method='name_filter', help_text=Help.name)
    status = filters.CharFilter(method='status_filter', help_text=Help.status)

    class Meta:
        """
        applying filters on fields
        we can also apply on custom fields
        """
        model = ScfUser
        fields = ['email', 'first_name', 'last_name', 'name', 'status']

    def name_filter(self, queryset, name, value):
        """
        /users?name=<name>
        """

        def full_name_test(user, full_name):
            """filter by full name"""
            return full_name in user.full_name.lower()

        full_name = value.lower()
        matches = [user.id for user in queryset.all() if full_name_test(user, full_name)]
        return ScfUser.objects.filter(id__in=matches)

    def status_filter(self, queryset, name, value):
        """
        /users?status=all|inactive|active
        """
        if value != 'all':
            if value in ['active', 'inactive']:
                is_active = value == 'active'
                return queryset.filter(is_active=is_active)

            else:
                raise ParseError("Value {} for query param {} is invalid.  "
                                 "Should be one of: all, active, or inactive.".format(value, name))
        return queryset
