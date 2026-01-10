from rest_framework import viewsets, decorators, response, permissions
from .models import Receipt


class ReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Receipt.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # filter by tenant/user in real app
        return response.Response({'results': []})

    @decorators.action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        # placeholder to return presigned URL
        return response.Response({'url': 'https://s3.example.com/receipt.pdf'})

    @decorators.action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        return response.Response({'status': 'resent'})
