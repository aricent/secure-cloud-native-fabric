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
