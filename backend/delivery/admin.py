from django.contrib import admin
from tenants.admin_utils import TenantAdminMixin
from .models import Delivery, DeliveryPersonnel, Address, ShippingFeeRule


class DeliveryPersonnelAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'phone', 'active', 'created_at')
    search_fields = ('name', 'phone')


class AddressAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'line1', 'city', 'zone', 'created_at')
    search_fields = ('label', 'line1', 'city', 'zone')
    list_filter = ('zone',)


class ShippingFeeRuleAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('zone', 'base_fee', 'per_km_fee', 'min_distance', 'max_distance', 'created_at')
    search_fields = ('zone',)
    list_filter = ('zone',)


@admin.register(Delivery)
class DeliveryAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ('order_reference', 'tracking_number', 'status', 'delivery_person', 'fee', 'created_at', 'updated_at')
    search_fields = ('order_reference', 'tracking_number')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_picked_up', 'mark_in_transit', 'mark_delivered', 'mark_failed']

    def mark_picked_up(self, request, queryset):
        for delivery in queryset:
            delivery.mark_picked_up()
        self.message_user(request, f"{queryset.count()} deliveries marked as picked up")
    mark_picked_up.short_description = "Mark selected as picked up"

    def mark_in_transit(self, request, queryset):
        for delivery in queryset:
            delivery.mark_in_transit()
        self.message_user(request, f"{queryset.count()} deliveries marked as in transit")
    mark_in_transit.short_description = "Mark selected as in transit"

    def mark_delivered(self, request, queryset):
        for delivery in queryset:
            delivery.mark_delivered()
        self.message_user(request, f"{queryset.count()} deliveries marked as delivered")
    mark_delivered.short_description = "Mark selected as delivered"

    def mark_failed(self, request, queryset):
        for delivery in queryset:
            delivery.mark_failed()
        self.message_user(request, f"{queryset.count()} deliveries marked as failed")
    mark_failed.short_description = "Mark selected as failed"


admin.site.register(DeliveryPersonnel, DeliveryPersonnelAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(ShippingFeeRule, ShippingFeeRuleAdmin)
