"""
We don't need filters on put/delete/retrieve so
we have override default Auto schema class get_link method
"""

from rest_framework.schemas import AutoSchema
from django.utils.six.moves.urllib import parse as urlparse
import coreapi


class CustomAutoSchema(AutoSchema):
    """
    We can override default django rest framework schema
    """
    def get_link(self, path, method, base_url):
        """ Here we are overriding get_link method """
        fields = self.get_path_fields(path, method)
        fields += self.get_serializer_fields(path, method)
        fields += self.get_pagination_fields(path, method)
        if self.view.action in ['list']:
            fields += self.get_filter_fields(path, method)

        manual_fields = self.get_manual_fields(path, method)
        fields = self.update_fields(fields, manual_fields)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method)
        else:
            encoding = None

        description = self.get_description(path, method)

        if base_url and path.startswith('/'):
            path = path[1:]

        return coreapi.Link(
            url=urlparse.urljoin(base_url, path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=description
        )
