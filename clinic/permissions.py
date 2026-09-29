from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCreatorOrReadOnly(BasePermission):
    """Anyone authenticated may read doctor records; only creator may change them."""

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.created_by_id == request.user.id
