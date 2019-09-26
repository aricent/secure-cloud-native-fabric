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
