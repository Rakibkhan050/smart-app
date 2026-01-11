from django.contrib import admin


class TenantAdminMixin:
    """Admin mixin to scope objects by the request user's tenant and auto-assign tenant on save.

    Behavior:
    - Non-superusers see only objects belonging to their `request.user.tenant`.
    - On create, the object's `tenant` will be set to `request.user.tenant` if available.
    """

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = getattr(request, 'user', None)
        # Superusers see everything
        if user and user.is_superuser:
            return qs
        # If user has a tenant FK, filter by it
        tenant = getattr(user, 'tenant', None)
        if tenant is not None:
            return qs.filter(tenant=tenant)
        return qs.none()

    def save_model(self, request, obj, form, change):
        user = getattr(request, 'user', None)
        if not change:
            tenant = getattr(user, 'tenant', None)
            if tenant is not None and hasattr(obj, 'tenant'):
                setattr(obj, 'tenant', tenant)
        return super().save_model(request, obj, form, change)
