from django.contrib import admin
from .models import Receipt


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'payment_id', 'amount', 's3_url', 'created_at')
