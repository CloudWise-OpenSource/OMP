from django.conf import settings
from rest_framework.permissions import BasePermission


class GetDataJsonAuthenticated(BasePermission):
    """
    Allows access only for users who with secret or authentication .
    """

    def has_permission(self, request, view):
        query_field = request.query_params.get("secret", "")
        return query_field == settings.DATA_JSON_SECRET or \
            bool(request.user and request.user.is_authenticated)
