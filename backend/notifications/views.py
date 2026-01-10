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
        # Save or update a web-push subscription for the current user
        data = request.data
        endpoint = data.get('endpoint')
        keys = data.get('keys', {})
        if not endpoint:
            return response.Response({'error': 'endpoint required'}, status=400)
        from .models import Subscription
        sub, created = Subscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={'keys': keys}
        )
        return response.Response({'status': 'subscribed', 'created': created})

    @decorators.action(detail=False, methods=['post'])
    def send_demo(self, request):
        # send a demo push to all of the user's subscriptions
        from .models import Subscription
        subs = Subscription.objects.filter(user=request.user)
        payload = request.data.get('payload', 'Demo notification')
        from .utils import send_web_push
        results = []
        for s in subs:
            ok = send_web_push({'endpoint': s.endpoint, 'keys': s.keys}, payload)
            results.append({'endpoint': s.endpoint, 'ok': ok})
        return response.Response({'results': results})
