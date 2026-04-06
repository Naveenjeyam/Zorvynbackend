from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only Admin role users can access."""
    message = "Access denied. Admin role required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.role == "admin"
        )


class IsAnalystOrAdmin(BasePermission):
    """Analyst or Admin role users can access."""
    message = "Access denied. Analyst or Admin role required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.role in ("analyst", "admin")
        )


class IsAnyRole(BasePermission):
    """Any authenticated active user can access (Viewer, Analyst, Admin)."""
    message = "Access denied. Active account required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admins can do everything.
    Others can only use safe methods (GET, HEAD, OPTIONS).
    """
    message = "Access denied. Admin role required for write operations."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_active):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role == "admin"
