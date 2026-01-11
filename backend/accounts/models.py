from django.db import models
from django.contrib.auth.models import AbstractUser
from tenants.models import Tenant


class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        # legacy/others
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    def has_role(self, *roles):
        return self.role in roles or self.is_superuser

    @property
    def is_owner(self):
        return self.has_role('owner')
    @property
    def is_admin(self):
        return self.has_role('admin')
    @property
    def is_manager(self):
        return self.has_role('manager')
    @property
    def is_cashier(self):
        return self.has_role('cashier')
