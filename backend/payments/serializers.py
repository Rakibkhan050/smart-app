from rest_framework import serializers
from .models import Payment, Receipt


class PaymentSerializer(serializers.ModelSerializer):
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id', 'payment_id', 'provider', 'status', 'amount', 'currency', 'metadata', 'created_at', 'receipt_url']
        read_only_fields = ['id', 'created_at']

    def get_receipt_url(self, obj):
        try:
            r = obj.get_receipt()
            if r:
                return r.get_presigned_url() or r.s3_url
        except Exception:
            return None
        return None


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ['id', 'invoice_no', 'payment_id', 'amount', 'vat_amount', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']
