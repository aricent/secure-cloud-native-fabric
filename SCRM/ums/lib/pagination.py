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
Here we've added scf custom pagination class
we can use these classes as per our need
"""

from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """
    Scf pagination defaults
    """

    # default to large page size until front end implements pagination links
    page_size = 100
    page_query_param = 'page_number'
    page_size_query_param = 'page_size'


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_query_param = 'page_number'
    page_size_query_param = 'page_size'
