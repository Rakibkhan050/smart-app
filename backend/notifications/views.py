from rest_framework import viewsets, decorators, response, permissions
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # simple: filter to the current user
        return self.queryset.filter(recipient=self.request.user)

    @decorators.action(detail=False, methods=['post'])
    def mark_read(self, request):
        ids = request.data.get('ids', [])
        qs = self.get_queryset().filter(id__in=ids)
        qs.update(read=True)
        return response.Response({'status': 'ok'})

    @decorators.action(detail=False, methods=['post'])
    def subscribe(self, request):
        # Placeholder for saving push subscription info
        return response.Response({'status': 'subscribed'})
