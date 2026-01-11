from rest_framework import permissions


class RolesAllowed(permissions.BasePermission):
    """Permission that checks a view's `allowed_roles` attribute (list) or `allowed_action_roles` mapping for actions.

    Usage:
      - set `allowed_roles = ['owner', 'admin']` on the view (applies to all actions), or
      - set `allowed_action_roles = {'create': ['owner','admin'], 'pay': ['cashier','manager']}` for per-action control.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # superusers bypass
        if getattr(request.user, 'is_superuser', False):
            return True

        # per-action mapping
        action = getattr(view, 'action', None)
        action_roles_map = getattr(view, 'allowed_action_roles', None)
        if action_roles_map and action in action_roles_map:
            return request.user.role in action_roles_map.get(action, [])

        # global allowed roles
        allowed = getattr(view, 'allowed_roles', None)
        if allowed is None:
            # default to allow authenticated users
            return True
        return request.user.role in allowed