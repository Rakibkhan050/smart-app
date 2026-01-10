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
        # Return presigned GET URL for the receipt if stored in S3
        try:
            receipt = self.get_queryset().get(pk=pk)
        except Receipt.DoesNotExist:
            return response.Response({'error': 'not found'}, status=404)
        if receipt.s3_url:
            import boto3
            from django.conf import settings
            s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                              endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                              region_name=settings.AWS_S3_REGION_NAME)
            # assume s3_url contains key stored as path after bucket
            key = receipt.s3_url.split('/')[-1]
            url = s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key}, ExpiresIn=3600)
            return response.Response({'url': url})
        return response.Response({'error': 'no file'}, status=400)

    @decorators.action(detail=False, methods=['post'])
    def presign_upload(self, request):
        filename = request.data.get('filename')
        content_type = request.data.get('content_type', 'application/pdf')
        if not filename:
            return response.Response({'error': 'filename required'}, status=400)
        import boto3
        from django.conf import settings
        s3 = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                          endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                          region_name=settings.AWS_S3_REGION_NAME)
        key = f"receipts/{filename}"
        url = s3.generate_presigned_url('put_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': key, 'ContentType': content_type}, ExpiresIn=3600)
        return response.Response({'url': url, 'key': key})

    @decorators.action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        return response.Response({'status': 'resent'})
